#!/usr/bin/env python3
"""
BMAD Autoresearch Experiment Controller
========================================
Autonomous research loop for Agent Zero + BMAD plugin optimization.
Edits ONE thing per experiment, benchmarks, keeps improvements.

This is the BMAD equivalent of Karpathy's autoresearch — instead of
training a GPT for 5 minutes, we run BMAD benchmark tasks via the A0
API and score the output with an LLM judge. No GPU needed.

Usage:
    python run_autoresearch.py --baseline          # record baseline first
    python run_autoresearch.py --exp N [--task id] # run N experiments
    python run_autoresearch.py --scores            # show leaderboard
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
PLUGIN_ROOT   = Path(__file__).parent
RESULTS_TSV   = PLUGIN_ROOT / "bmad_results.tsv"
BENCHMARK_CMD = [sys.executable, str(PLUGIN_ROOT / "benchmark" / "run_suite.py")]
TSV_HEADER    = "commit\tbmad_score\tstatus\tdescription\ttask_scores\ttimestamp\n"


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(*args, cwd=None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True,
        cwd=str(cwd or PLUGIN_ROOT)
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def current_commit() -> str:
    return git("rev-parse", "--short", "HEAD")


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD")


def has_uncommitted_changes() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "HEAD"],
        cwd=str(PLUGIN_ROOT)
    )
    return result.returncode != 0


def commit_changes(message: str) -> str:
    """Stage all tracked changes and commit. Returns new commit hash."""
    git("add", "-u")  # only stage already-tracked files
    git("commit", "-m", message)
    return current_commit()


def discard_changes():
    """Undo last commit and restore working tree."""
    git("reset", "--hard", "HEAD~1")


# ── Results tracking ──────────────────────────────────────────────────────────

def init_results():
    """Create results TSV with header if it doesn't exist."""
    if not RESULTS_TSV.exists():
        RESULTS_TSV.write_text(TSV_HEADER, encoding="utf-8")
        print(f"📋 Created {RESULTS_TSV}")


def append_result(commit: str, score: float, status: str, description: str, task_scores: dict):
    """Append one row to bmad_results.tsv."""
    task_summary = "|".join(
        f"{t['id']}={t['score']:.3f}" for t in task_scores.get("tasks", [])
    )
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    row = f"{commit}\t{score:.4f}\t{status}\t{description}\t{task_summary}\t{timestamp}\n"
    with open(RESULTS_TSV, "a", encoding="utf-8") as f:
        f.write(row)


def best_score() -> float:
    """Return the current best bmad_score from results.tsv."""
    if not RESULTS_TSV.exists():
        return 0.0
    best = 0.0
    with open(RESULTS_TSV, encoding="utf-8") as f:
        for line in f:
            if line.startswith("commit"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 3 and parts[2] == "keep":
                try:
                    best = max(best, float(parts[1]))
                except ValueError:
                    pass
    return best


def show_leaderboard():
    """Print sorted results table."""
    if not RESULTS_TSV.exists():
        print("No results yet. Run --baseline first.")
        return
    rows = []
    with open(RESULTS_TSV, encoding="utf-8") as f:
        for line in f:
            if line.startswith("commit"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                rows.append(parts)
    rows.sort(key=lambda r: float(r[1]) if r[1].replace(".","").isdigit() else 0, reverse=True)
    print(f"\n{'#':>3} {'commit':>8} {'score':>8} {'status':>8}  description")
    print("-" * 70)
    for i, r in enumerate(rows):
        status_icon = "✅" if r[2] == "keep" else "❌"
        print(f"{i+1:>3} {r[0]:>8} {float(r[1]):>8.4f} {status_icon} {r[2]:>6}  {r[3][:50]}")
    print(f"\n  Best score: {best_score():.4f}")
    print(f"  Total experiments: {len(rows)}")


# ── Benchmark runner ──────────────────────────────────────────────────────────

def run_benchmark(task_filter=None) -> tuple[float, dict]:
    """Run the benchmark suite. Returns (bmad_score, full_result_dict)."""
    cmd = BENCHMARK_CMD.copy()
    if task_filter:
        cmd += ["--task", task_filter]

    print(f"  🔬 Running benchmark: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    # stderr contains human-readable progress
    if result.stderr:
        for line in result.stderr.strip().split("\n"):
            print(f"     {line}")

    if result.returncode != 0:
        print(f"  ❌ Benchmark failed (rc={result.returncode})")
        return 0.0, {}

    try:
        data = json.loads(result.stdout.strip())
        return data["bmad_score"], data
    except Exception as e:
        print(f"  ❌ Cannot parse benchmark output: {e}")
        print(f"  stdout: {result.stdout[:500]}")
        return 0.0, {}


# ── Baseline ──────────────────────────────────────────────────────────────────

def run_baseline():
    """Record the baseline score for the current plugin state."""
    print("\n📌 Recording BASELINE...")
    init_results()

    commit = current_commit()
    score, data = run_benchmark()

    append_result(
        commit=commit,
        score=score,
        status="keep",
        description="baseline — unmodified plugin",
        task_scores=data,
    )
    print(f"\n✅ Baseline recorded: bmad_score={score:.4f} (commit={commit})")
    print(f"   Results: {RESULTS_TSV}")
    return score


# ── Experiment loop ───────────────────────────────────────────────────────────

def run_experiment(exp_num: int, description: str, task_filter=None) -> dict:
    """
    Run one experiment:
    - Assumes the caller has already edited one file in the plugin
    - Commits the change, runs benchmark, keeps or discards
    Returns result dict with score and status
    """
    print(f"\n{'='*60}")
    print(f"🧪 Experiment #{exp_num}: {description}")
    print(f"{'='*60}")

    # Check there's something to commit
    if not has_uncommitted_changes():
        print("  ⚠️  No uncommitted changes found — skipping")
        return {"status": "skip", "score": 0.0}

    # Commit the change
    commit_msg = f"exp #{exp_num}: {description}"
    try:
        commit = commit_changes(commit_msg)
        print(f"  📝 Committed: {commit} — {commit_msg}")
    except Exception as e:
        print(f"  ❌ Commit failed: {e}")
        return {"status": "error", "score": 0.0}

    # Record current best before this experiment
    prev_best = best_score()
    print(f"  📊 Previous best: {prev_best:.4f}")

    # Run benchmark
    start = time.time()
    score, data = run_benchmark(task_filter=task_filter)
    elapsed = time.time() - start

    print(f"  ⏱️  Benchmark took {elapsed:.0f}s")
    print(f"  📈 New score: {score:.4f} vs best: {prev_best:.4f}")

    # Decision: keep if strictly better
    if score > prev_best:
        status = "keep"
        delta = score - prev_best
        print(f"  ✅ KEEP! Improvement: +{delta:.4f}")
    else:
        status = "discard"
        delta = score - prev_best
        print(f"  ❌ DISCARD. Delta: {delta:.4f}")
        discard_changes()
        print(f"  ↩️  Reverted to previous commit")

    # Log result (even discards — useful for learning)
    append_result(
        commit=commit if status == "keep" else "discarded",
        score=score,
        status=status,
        description=description,
        task_scores=data,
    )

    return {
        "status": status,
        "score": score,
        "prev_best": prev_best,
        "delta": delta,
        "elapsed": elapsed,
        "commit": commit if status == "keep" else None,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BMAD Autoresearch Controller")
    parser.add_argument("--baseline", action="store_true", help="Record baseline score")
    parser.add_argument("--exp", type=int, default=0, help="Number of experiments to run")
    parser.add_argument("--task", help="Only run specific benchmark task")
    parser.add_argument("--scores", action="store_true", help="Show leaderboard")
    parser.add_argument("--desc", default="manual experiment", help="Experiment description")
    args = parser.parse_args()

    print(f"\n🤖 BMAD Autoresearch Controller")
    print(f"   Plugin: {PLUGIN_ROOT}")
    print(f"   Branch: {current_branch()}")
    print(f"   Commit: {current_commit()}")
    print(f"   Best:   {best_score():.4f}")

    if args.baseline:
        run_baseline()

    elif args.scores:
        show_leaderboard()

    elif args.exp > 0:
        # This is called by Agent Zero after it edits one file
        result = run_experiment(
            exp_num=args.exp,
            description=args.desc,
            task_filter=args.task,
        )
        # Output JSON for Agent Zero to parse
        print(json.dumps(result))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
