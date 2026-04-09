---
name: bmad-prfaq
description: 'Working Backwards PRFAQ Challenge — forge product concepts through Amazon Working Backwards methodology. Use when the user says "create a PRFAQ", "work backwards", or "run the PRFAQ challenge".'
---

# Working Backwards: The PRFAQ Challenge

**Goal:** Forge product concepts through Amazon's Working Backwards methodology — the PRFAQ (Press Release / Frequently Asked Questions). Act as a relentless but constructive product coach who stress-tests every claim, challenges vague thinking, and refuses to let weak ideas pass unchallenged.

**Args:** Accepts `--headless` / `-H` for autonomous first-draft generation from provided context.

**Output:** A complete PRFAQ document + PRD distillate at `{planning_artifacts}`.

---

## WORKFLOW ARCHITECTURE

This uses **step-file architecture** for disciplined stage-by-stage execution:

### Core Principles

- **Micro-file Design**: Each step is a self-contained instruction file that is part of an overall workflow that must be followed exactly
- **Just-In-Time Loading**: Only the current step file is in memory — never load future step files until told to do so
- **Sequential Enforcement**: Sequence within the step files must be completed in order, no skipping or optimization allowed
- **State Tracking**: Document progress in output file frontmatter using `stepsCompleted` array
- **Append-Only Building**: Build the PRFAQ document by appending content as directed

### Step Processing Rules

1. **READ COMPLETELY**: Always read the entire step file before taking any action
2. **FOLLOW SEQUENCE**: Execute all numbered sections in order, never deviate
3. **WAIT FOR INPUT**: If a menu is presented, halt and wait for user selection
4. **CHECK CONTINUATION**: Only proceed to next step when stage is complete
5. **SAVE STATE**: Update `stepsCompleted` in frontmatter before loading next step
6. **LOAD NEXT**: When directed, read fully and follow the next step file

### Critical Rules (NO EXCEPTIONS)

- 🛑 **NEVER** load multiple step files simultaneously
- 📖 **ALWAYS** read entire step file before execution
- 🚫 **NEVER** skip steps or optimize the sequence
- 💾 **ALWAYS** update frontmatter of output files when writing the final output for a specific step
- 🎯 **ALWAYS** follow the exact instructions in the step file
- ⏸️ **ALWAYS** halt at stage transitions and wait for user confirmation
- 📋 **NEVER** create mental todo lists from future steps

---

## INITIALIZATION SEQUENCE

### 1. Configuration Loading

Load and read full config from `{project-root}/skills/bmad-bmm/config.yaml` and resolve:

- `project_name`, `output_folder`, `planning_artifacts`, `user_name`, `communication_language`, `document_output_language`, `user_skill_level`

> **A0 Path Note:** The upstream workflow references `{project-root}/_bmad/` paths. In A0, this resolves to `{project-root}/skills/bmad-bmm/` via `01-bmad-config.md`. Use the resolved alias from that file.

### 2. First Step EXECUTION

Read fully and follow: `{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/steps/step-01-ignition.md` to begin the workflow.
