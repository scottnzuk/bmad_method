#!/usr/bin/env python3
"""
BMAD Autoresearch Benchmark Runner
===================================
Runs all benchmark tasks against the live Agent Zero + BMAD plugin,
scores outputs via LLM-as-judge, and returns a single bmad_score (0.0-1.0).

Usage:
    python benchmark/run_suite.py [--task task_01] [--verbose]

Outputs JSON to stdout:
    {"bmad_score": 0.73, "tasks": [{"id": ..., "score": ..., "reason": ...}]}
"""

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import requests
import yaml

# ── Config ────────────────────────────────────────────────────────────────────
A0_BASE  = os.environ.get("A0_BASE", "http://localhost:80")
A0_LOGIN = os.environ.get("AUTH_LOGIN", "")
A0_PASS  = os.environ.get("AUTH_PASSWORD", "")
TASKS_FILE = Path(__file__).parent / "tasks.yaml"
MAX_WAIT_SEC = 300       # max seconds to wait for agent response
POLL_INTERVAL = 3        # seconds between polling

# ── Session with CSRF handling ────────────────────────────────────────────────

def make_session() -> tuple[requests.Session, str]:
    """Create an authenticated session and fetch CSRF token."""
    sess = requests.Session()
    sess.headers.update({"Origin": "http://localhost:80"})

    # Step 1: Login if credentials are set
    if A0_LOGIN and A0_PASS:
        login_resp = sess.post(
            f"{A0_BASE}/login",
            data={"username": A0_LOGIN, "password": A0_PASS},
            allow_redirects=True,
            timeout=10,
        )
        if "/login" in login_resp.url:
            raise RuntimeError(f"Login failed — check AUTH_LOGIN/AUTH_PASSWORD env vars")
        print(f"   Logged in as {A0_LOGIN} ✓", file=sys.stderr)

    # Step 2: Fetch CSRF token
    resp = sess.get(f"{A0_BASE}/api/csrf_token", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"CSRF token error: {data}")
    token = data.get("token", "")
    sess.headers.update({"X-CSRF-Token": token})
    return sess, token


def create_context(sess: requests.Session) -> str:
    """Create a fresh isolated chat context for one benchmark task."""
    new_ctxid = str(uuid.uuid4()).replace("-", "")[:16]
    resp = sess.post(
        f"{A0_BASE}/api/chat_create",
        json={"new_context": new_ctxid},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["ctxid"]


def send_message(sess: requests.Session, ctxid: str, text: str) -> str:
    """Send a message to a context and wait for full agent response."""
    # Send message (blocking endpoint waits for full response)
    resp = sess.post(
        f"{A0_BASE}/api/message",
        json={"text": text, "context": ctxid},
        timeout=MAX_WAIT_SEC,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", "")


# ── LLM-as-Judge ─────────────────────────────────────────────────────────────

def llm_judge(task: dict, agent_response: str) -> dict:
    """
    Use litellm/anthropic to score agent output against task criteria.
    Returns {score: 0.0-1.0, criteria_scores: [...], reason: str}
    """
    try:
        import litellm
    except ImportError:
        # Fallback: simple keyword scoring if litellm not available
        return keyword_judge(task, agent_response)

    criteria = task.get("criteria", [])
    criteria_text = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(criteria))

    judge_prompt = f"""You are an expert evaluator assessing an AI agent's response.

TASK GIVEN TO AGENT:
{task['prompt']}

EVALUATION CRITERIA (each must be met to score 1.0):
{criteria_text}

AGENT RESPONSE:
{agent_response[:4000]}

For each criterion, output a line: CRITERION_N: PASS or FAIL and why.
Then output: OVERALL_SCORE: X.X (0.0 to 1.0, where 1.0 = all criteria met)
Then output: SUMMARY: one line explanation."""

    try:
        response = litellm.completion(
            model=os.environ.get("JUDGE_MODEL", "anthropic/claude-3-5-haiku-20241022"),
            messages=[{"role": "user", "content": judge_prompt}],
            max_tokens=500,
            temperature=0,
        )
        judge_text = response.choices[0].message.content
        return parse_judge_output(judge_text, criteria)
    except Exception as e:
        print(f"  [judge error: {e}] falling back to keyword scoring", file=sys.stderr)
        return keyword_judge(task, agent_response)


def parse_judge_output(text: str, criteria: list) -> dict:
    """Parse LLM judge output into structured score."""
    lines = text.strip().split("\n")
    criteria_scores = []
    score = 0.0
    summary = ""

    passes = 0
    for line in lines:
        if line.startswith("CRITERION_"):
            passed = ": PASS" in line.upper()
            criteria_scores.append({"pass": passed, "detail": line})
            if passed:
                passes += 1
        elif line.startswith("OVERALL_SCORE:"):
            try:
                score = float(line.split(":")[1].strip())
            except Exception:
                score = passes / max(len(criteria), 1)
        elif line.startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()

    if not criteria_scores:
        score = passes / max(len(criteria), 1)

    return {"score": score, "criteria_scores": criteria_scores, "reason": summary}


def keyword_judge(task: dict, response: str) -> dict:
    """Simple keyword-based fallback judge."""
    criteria = task.get("criteria", [])
    resp_lower = response.lower()
    passes = 0
    criteria_scores = []

    keyword_map = {
        "phase 1": "phase 1" in resp_lower or "analysis" in resp_lower,
        "prd": "prd" in resp_lower or "product requirements" in resp_lower,
        "user stor": "as a" in resp_lower and "i want" in resp_lower,
        "acceptance criteria": "acceptance criteria" in resp_lower,
        "api endpoint": "endpoint" in resp_lower or "get /" in resp_lower or "post /" in resp_lower,
        "memory_save": "memory_save" in response or "memorize" in resp_lower,
        "test": "def test_" in response or "assert" in response,
    }

    for criterion in criteria:
        passed = any(
            kw in criterion.lower() and hit
            for kw, hit in keyword_map.items()
        ) or len(response) > 200  # at least produced substantive output
        criteria_scores.append({"pass": passed, "detail": criterion})
        if passed:
            passes += 1

    score = passes / max(len(criteria), 1)
    return {"score": round(score, 3), "criteria_scores": criteria_scores, "reason": f"keyword match: {passes}/{len(criteria)}"}


# ── Benchmark Runner ──────────────────────────────────────────────────────────

def run_task(sess: requests.Session, task: dict, verbose: bool = False) -> dict:
    """Run a single benchmark task and return scored result."""
    task_id = task["id"]
    agent = task.get("agent", "bmad-master")
    prompt = task["prompt"].strip()
    weight = task.get("weight", 1.0)

    print(f"  [{task_id}] {task['name']} → {agent}", file=sys.stderr)

    # Create isolated context
    ctxid = create_context(sess)

    # Prefix message to activate correct BMAD agent profile
    full_prompt = f"""[BENCHMARK TASK - respond as {agent} specialist]

{prompt}"""

    start = time.time()
    try:
        response = send_message(sess, ctxid, full_prompt)
        elapsed = time.time() - start
    except Exception as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        return {
            "id": task_id,
            "name": task["name"],
            "agent": agent,
            "score": 0.0,
            "weight": weight,
            "reason": f"ERROR: {e}",
            "response_len": 0,
            "elapsed_sec": 0,
        }

    if verbose:
        print(f"\n--- RESPONSE ({len(response)} chars, {elapsed:.1f}s) ---", file=sys.stderr)
        print(response[:1000], file=sys.stderr)
        print("---", file=sys.stderr)

    # Score the response
    judge_result = llm_judge(task, response)
    score = judge_result["score"]

    print(f"    score={score:.3f} reason={judge_result['reason'][:80]} ({elapsed:.1f}s)", file=sys.stderr)

    return {
        "id": task_id,
        "name": task["name"],
        "agent": agent,
        "score": score,
        "weight": weight,
        "reason": judge_result["reason"],
        "criteria_scores": judge_result.get("criteria_scores", []),
        "response_len": len(response),
        "elapsed_sec": round(elapsed, 1),
        "ctxid": ctxid,
    }


def run_suite(task_filter: Optional[str] = None, verbose: bool = False) -> dict:
    """Run the full benchmark suite and return aggregated scores."""
    # Load tasks
    with open(TASKS_FILE) as f:
        config = yaml.safe_load(f)
    tasks = config["tasks"]

    if task_filter:
        tasks = [t for t in tasks if t["id"] == task_filter]
        if not tasks:
            print(f"ERROR: task '{task_filter}' not found", file=sys.stderr)
            sys.exit(1)

    print(f"\n🔬 BMAD Benchmark Suite — {len(tasks)} tasks", file=sys.stderr)
    print(f"   Target: {A0_BASE}", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    # Setup session
    try:
        sess, token = make_session()
        print(f"   CSRF token: {token[:16]}...", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Cannot connect to A0 at {A0_BASE}: {e}", file=sys.stderr)
        sys.exit(1)

    # Run all tasks
    results = []
    for task in tasks:
        result = run_task(sess, task, verbose=verbose)
        results.append(result)
        time.sleep(2)  # brief pause between tasks

    # Compute weighted average bmad_score
    total_weight = sum(r["weight"] for r in results)
    weighted_sum = sum(r["score"] * r["weight"] for r in results)
    bmad_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    print("-" * 60, file=sys.stderr)
    print(f"\n✅ bmad_score: {bmad_score:.4f}", file=sys.stderr)
    print("   Task scores:", file=sys.stderr)
    for r in results:
        status = "✅" if r["score"] >= 0.7 else "⚠️" if r["score"] >= 0.4 else "❌"
        print(f"   {status} {r['id']}: {r['score']:.3f} — {r['reason'][:60]}", file=sys.stderr)

    output = {
        "bmad_score": round(bmad_score, 4),
        "tasks": results,
        "total_tasks": len(results),
        "passed": sum(1 for r in results if r["score"] >= 0.7),
    }

    # Print JSON to stdout (machine-readable)
    print(json.dumps(output))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BMAD Benchmark Suite Runner")
    parser.add_argument("--task", help="Run single task by ID (e.g. task_01)")
    parser.add_argument("--verbose", action="store_true", help="Show agent responses")
    args = parser.parse_args()

    run_suite(task_filter=args.task, verbose=args.verbose)
