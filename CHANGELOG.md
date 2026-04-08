# Changelog

All notable changes to the BMAD Method plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.2] — 2026-04-08

### Upstream Source Updates

**Core (BMM): 6.0.4 → 6.2.2**

- `code-review` workflow: full rewrite with sharded 4-step architecture (step-01 through step-04 + workflow.md), replacing the old workflow.yaml format
- `quick-dev` workflow: overhauled with new flat step structure (step-01 through step-05 + step-oneshot.md + spec-template.md)
- `checkpoint-preview`: new Phase 4 workflow added — LLM-assisted human-in-the-loop review (5 steps)
- Source references updated in `.a0proj/bmad-source/core/`

**BMB (Builder): 1.1.0 → 1.5.0**

- `agent-builder`: sanctum memory architecture added (BOND/CREED/MEMORY/PERSONA/PULSE/INDEX templates + bootloader), 26 new reference docs, 8 updated scripts
- `workflow-builder`: 18 new reference docs added + Workflow Convert capability scripts
- `module-builder`: 10 new assets (standalone + setup-skill templates), references, scripts
- `bmb-setup`: new skill added (module setup scripts + module-help.csv)
- Source references updated in `.a0proj/bmad-source/bmb/`

**TEA (Test Architect): 1.7.2 → 1.9.1**

- 13 old `*subprocess*` step files deleted — renamed to `*subagent*` terminology across all 9 workflows
- `playwright-cli.md` knowledge fragment added to workflow knowledge directories
- All step files (steps-c / steps-e / steps-v) synced from upstream
- Source references updated in `.a0proj/bmad-source/tea/`

**CIS: 0.1.9** — no change

### CSV and Routing Fixes

- Renamed `agent` → `skill` column in all `module-help.csv` headers (8 files) to align with upstream 13-column spec
- Added `checkpoint-preview` (code: `CHK`) to `bmad-bmm/module-help.csv`
- Added `bmb-setup` (code: `BS`) to `bmad-bmb/module-help.csv`
- Fixed `code-review` CSV path: `workflow.yaml` → `workflow.md`
- Fixed `code-review` SKILL.md to reference `workflow.md`

### Tests

- Behavioral regression: 49/49 PASS (0 PARTIAL, 0 FAIL)
- Fixed test harness `load_module_help_csvs()` to use top-level CSV only, matching runtime extension behavior

### Documentation

- README fully rewritten — value-first, audience-focused, no internal implementation details
- plugin.yaml description updated to reflect current state

---

## [1.0.1] — 2026-03-27

### Routing Extension

- Implemented dynamic lightweight (LW) routing — the `LW` command now reads directly from `skills/*/module-help.csv` at runtime, eliminating the sync risk with the compiled `bmad-help.csv` aggregate
- `_80_bmad_routing_manifest.py` column priority fixed: reads the `agent` column (the original column name) with `skill` and `agent-name` retained as legacy fallbacks
- Natural language routing fallback updated to also use dynamic module CSVs instead of the compiled aggregate
- Removed `_11_bmad_autobrief.py` extension — A0 natively auto-injects all `.a0proj/instructions/` files into every agent's system prompt; the extension was redundant

### Documentation Sprint 1 (Stories 016–018)

- `project-overview.md` refreshed with current architecture and story table
- `project-context.md` generated (LLM-optimized brownfield context)
- Architecture v4.0 document written
- Retrospective PRD authored — dogfooding gap closed

### Update Sprint 1 (Stories 019–023)

- `module-help.csv` format updated to 13-column upstream spec across all modules
- `bmad-bmm` skill updated to include all Phase 4 workflows
- `bmad-bmb` skill updated to BMB v1.2.0 (major restructure)
- `bmad-tea` skill updated to TEA v1.7.2 (skills migration)
- `bmad-cis` skill updated to CIS v0.1.9 (skill format conversion)
- Per-workflow thin SKILL.md wrappers implemented (Option B)

---

## [1.0.0] — 2026-02-28

### Initial Release

- Full BMAD Method Framework integration for Agent Zero
- 20 specialist agents across 4 modules: BMM, BMB, TEA, CIS
- 5 skill packages with bundled workflow files
- Project-scoped FAISS-native shared memory store
- Phase-aware routing extension (`_80_bmad_routing_manifest.py`)
- Interactive BMAD status dashboard plugin
- Party Mode (single-LLM multi-persona simulation)
- `bmad-init` bootstrap script for workspace initialization
- Phase Gate Protocol (GATE-001) enforcement
