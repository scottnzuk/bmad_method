---
name: "bmad-cis"
description: "BMAD Creative Intelligence Suite — innovation, design thinking, storytelling, problem solving, brainstorming. Triggers: innovation strategy, disruption opportunities, design thinking, empathy driven design, storytelling, narrative, problem solving, structured problem solving, brainstorming, ideate, creative session, cis module."
version: "1.0.0"
author: "BMAD"
tags: ["bmad", "cis", "creative", "innovation", "design"]
trigger_patterns:
  - "innovation strategy"
  - "disruption opportunities"
  - "design thinking"
  - "empathy driven design"
  - "storytelling"
  - "narrative"
  - "problem solving"
  - "structured problem solving"
  - "brainstorming"
  - "ideate"
  - "creative session"
  - "cis module"
---

# BMAD Creative Intelligence Suite (CIS) — Innovation and Design Thinking

CIS provides structured creative methodologies: innovation strategy, design thinking, storytelling, and problem solving. Use CIS when you need creative rigor applied to product discovery, user research, or strategic challenges.

All paths use `{project-root}` which resolves to `.a0proj/` as defined in `01-bmad-config.md`.

When any CIS workflow is triggered, read the full workflow file at the path shown and follow it exactly.

---

## CIS Workflows

### Innovation Strategy
**Triggers:** "innovation strategy", "disruption opportunities", "strategic innovation", "innovation roadmap"
**Output artifact:** `{project-root}/_bmad-output/planning-artifacts/innovation-strategy-<date>.md`
**Workflow:** `{skill-dir}/workflows/innovation-strategy/workflow.yaml`

### Design Thinking
**Triggers:** "design thinking", "empathy driven design", "user centered design", "design sprint"
**Output artifact:** `{project-root}/_bmad-output/planning-artifacts/design-thinking-<date>.md`
**Workflow:** `{skill-dir}/workflows/design-thinking/workflow.yaml`

### Storytelling
**Triggers:** "storytelling", "narrative", "craft narrative", "story framework", "communication strategy"
**Output artifact:** `{project-root}/_bmad-output/planning-artifacts/storytelling-<date>.md`
**Workflow:** `{skill-dir}/workflows/storytelling/workflow.yaml`

### Problem Solving
**Triggers:** "problem solving", "structured problem solving", "brainstorming", "ideate", "creative session", "root cause analysis"
**Output artifact:** `{project-root}/_bmad-output/planning-artifacts/problem-solving-<date>.md`
**Workflow:** `{skill-dir}/workflows/problem-solving/workflow.yaml`

---


---

## Short Trigger Codes

Use these short codes or fuzzy phrases to activate CIS specialist agents directly:

| Code | Fuzzy Phrase | Agent | Description |
|------|-------------|-------|-------------|
| `BS` | brainstorm | bmad-brainstorming-coach (Carson) | Guide brainstorming session |
| `DT` | design-thinking | bmad-design-thinking (Maya) | Guide human-centered design process |
| `IS` | innovation-strategy | bmad-innovation (Victor) | Identify disruption opportunities |
| `PS` | problem-solving | bmad-problem-solver (Dr. Quinn) | Apply systematic problem-solving |
| `ST` | story | bmad-storyteller (Sophia) | Craft compelling narrative |
| `SD` | slide-deck | bmad-presentation (Caravaggio) | Create professional slide presentation |
| `EX` | youtube-explainer | bmad-presentation (Caravaggio) | Design YouTube/video explainer |
| `PD` | pitch-deck | bmad-presentation (Caravaggio) | Craft investor pitch deck |
| `CT` | conference-talk | bmad-presentation (Caravaggio) | Build conference talk materials |
| `IN` | infographic | bmad-presentation (Caravaggio) | Design information visualization |
| `VM` | visual-metaphor | bmad-presentation (Caravaggio) | Create conceptual illustrations |
| `CV` | concept-visual | bmad-presentation (Caravaggio) | Generate expressive concept image |

## Execution Instructions

When any CIS workflow is triggered:
1. Identify the workflow from the trigger phrase.
2. Read the full workflow file at the path shown above using `code_execution_tool` (bash cat).
3. Follow the workflow instructions exactly — do not summarize or skip steps.
4. Write output artifacts using `code_execution_tool` (bash write).
5. Update `{project-root}/instructions/02-bmad-state.md` to reflect the active CIS workflow.
