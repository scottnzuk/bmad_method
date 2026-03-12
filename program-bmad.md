# BMAD Autoresearch — Native Agent Zero Research Loop

## What You Are Doing
You are autonomously improving the BMAD Method plugin for Agent Zero.
Each experiment: edit ONE file → git commit → run benchmark (call_subordinate!) → measure bmad_score → keep or discard.
NEVER use HTTP API or subprocess. YOU are the benchmark runner.

## The Metric: bmad_score (0.0 → 1.0, higher is better)
- Weighted average of 6 task scores
- You run each task by calling the appropriate BMAD subordinate directly
- You grade each response yourself as LLM judge
- Baseline: record in `bmad_results.tsv` on first run

## Plugin Root
`/a0/usr/projects/a0_bmad_method/`

---

## Benchmark Tasks (run ALL 6 per experiment)

Load tasks from: `benchmark/tasks.yaml`

### How to run a benchmark task
1. `call_subordinate(profile="{task.agent}", reset=true, message="{task.prompt}")`
2. Read the subordinate's response
3. Grade each criterion: PASS (1) or FAIL (0)
4. Task score = passes / total_criteria
5. Record score

### How to compute bmad_score
```
weighted_sum = sum(task.score * task.weight for task in tasks)
total_weight = sum(task.weight for task in tasks)
bmad_score = weighted_sum / total_weight
```

### Grading criteria (be strict but fair)
- PASS: criterion is clearly and specifically met
- FAIL: criterion is absent, vague, or only partially met
- Do NOT give partial credit — each criterion is binary

---

## Experiment Loop (NEVER STOP)

### Step 1: Setup (once per session)
```bash
cd /a0/usr/projects/a0_bmad_method
git status
git log --oneline -3
cat bmad_results.tsv 2>/dev/null || echo 'No results yet'
```
Load memory: `memory_load("bmad autoresearch experiments results")`

### Step 2: Generate hypothesis
Choose ONE change to test. Priority:
1. **Agent context** (`agents/{profile}/agent.yaml` → `context:` block)
   - Add routing examples to bmad-master
   - Add output format templates to bmad-pm, bmad-architect
   - Strengthen TDD enforcement in bmad-dev
   - Add memory protocol examples
2. **Extension** (`extensions/python/*/`)
   - Tune routing manifest format
   - Adjust sidecar injection content
3. **Knowledge** (`knowledge/{agent}/`)
   - Add worked examples
   - Add scoring rubrics

### Step 3: Make ONE edit
```
text_editor:read → understand current content
text_editor:patch → make precise targeted change
```
NEVER edit: `benchmark/`, `run_autoresearch.py`, `bmad_results.tsv`
NEVER change multiple files

### Step 4: Commit the change
```bash
cd /a0/usr/projects/a0_bmad_method
git add -u
git commit -m "exp #N: {description}"
```
Note the commit hash.

### Step 5: Run the benchmark (6 tasks)
For EACH task in `benchmark/tasks.yaml`:
```
call_subordinate(
  profile="{task.agent}",
  reset=true,
  message="{task.prompt}"
)
```
Grade the response against `task.criteria`. Compute task score.

### Step 6: Compute bmad_score and decide
```python
# Weights: task_01=1.5, all others=1.0
weighted_sum = (score_01 * 1.5) + score_02 + score_03 + score_04 + score_05 + score_06
bmad_score = weighted_sum / 6.5
```

Compare to previous best (from bmad_results.tsv):
- **Improved** → KEEP, continue
- **Same or worse** → DISCARD:
  ```bash
  git reset --hard HEAD~1
  ```

### Step 7: Record result
```bash
# Append to bmad_results.tsv (TAB separated, NEVER commit this file)
echo "{commit}\t{bmad_score:.4f}\t{keep|discard}\t{description}\t{task_scores}" >> bmad_results.tsv
```

### Step 8: Save to memory
```
memory_save: "[BMAD-RESEARCH] exp #N: {hypothesis} → bmad_score={X:.4f} delta={±X:.4f} {keep|discard}\nTask breakdown: 01={x} 02={x} 03={x} 04={x} 05={x} 06={x}\nInsight: {what you learned}\nNext: {2-3 follow-up ideas}"
```

### Step 9: GOTO Step 2

---

## Quick Reference: Task Agents

| Task | Profile | Weight |
|------|---------|--------|
| task_01_routing | bmad-master | 1.5 |
| task_02_prd | bmad-pm | 1.0 |
| task_03_architecture | bmad-architect | 1.0 |
| task_04_story | bmad-sm | 1.0 |
| task_05_memory_protocol | bmad-architect | 1.0 |
| task_06_dev_tdd | bmad-dev | 1.0 |

---

## Simplicity Rule
- Equal score + fewer lines of change → KEEP the simpler one
- +0.02 improvement + 50 lines of verbose instructions → DISCARD
- +0.02 improvement + DELETE 10 lines → always KEEP

## Important Rules
- ONE file change per experiment, no exceptions
- ALWAYS run ALL 6 tasks, not just the ones you expect to improve
- NEVER stop the loop unless user asks
- Do NOT rely on memory alone for decisions — always recheck bmad_results.tsv
- Do NOT commit bmad_results.tsv — it is a local log only
