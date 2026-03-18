# BMAD Method — Installation Guide

← [Back to README](README.md)

This guide covers installation, verification, first run, developer setup, upgrade procedures, and troubleshooting for the BMAD Method plugin for Agent Zero.

---

## Prerequisites

- [Agent Zero](https://github.com/frdel/agent-zero) installed and running (latest stable release)
- An LLM with a large context window is strongly recommended — **Claude Sonnet or better**
- Git (for Option A) or file access to copy the plugin folder

---

## Option A — Clone Directly into Agent Zero (Production)

Clone the repository directly into Agent Zero's plugin directory:

```bash
git clone https://github.com/vanja-emichi/bmad_method.git /path/to/agent-zero/usr/plugins/bmad
```

Replace `/path/to/agent-zero` with your actual Agent Zero installation path (e.g. `/a0`).

> [!WARNING]
> **The plugin folder MUST be named `bmad`** — not `bmad_method`, `a0-bmad-method`, or anything else. The dashboard and extensions reference `/usr/plugins/bmad/` internally. An incorrectly named folder causes silent extension loading failures and dashboard breakage.

---

## Option B — Copy from an Existing Clone (Production)

If you have already cloned the repository elsewhere:

```bash
cp -r /path/to/bmad_method /path/to/agent-zero/usr/plugins/bmad
```

> [!WARNING]
> **The destination folder MUST be named `bmad`** — see warning above.

---

## Post-Install Verification

1. **Restart Agent Zero** — the plugin is read on startup
2. Open the Agent Zero settings or plugin panel
3. Confirm **BMAD Method** appears in the plugin list and is enabled
4. The `.toggle-1` file is included in the repo, so the plugin ships **pre-enabled** — you should not need to manually enable it
5. Confirm the **BMAD sidebar button** appears in the Agent Zero UI

If the plugin does not appear, see [Troubleshooting](#troubleshooting) below.

---

## First Run — `bmad init`

After installation, open Agent Zero and select the **BMad Master** profile. Then type:

```
bmad init
```

This triggers the `bmad-init` skill which sets up the BMAD workspace for your project inside `.a0proj/`.

### What `bmad init` Creates

| Path | Description |
|------|-------------|
| `.a0proj/instructions/01-bmad-config.md` | Path aliases and user settings for this project |
| `.a0proj/instructions/02-bmad-state.md` | Current BMAD phase, active persona, and artifact tracking |
| `.a0proj/_bmad-output/` | Output directory for all generated planning and implementation artifacts |
| `.a0proj/knowledge/` | Project knowledge base directory (FAISS-preloaded on each session) |

### Successful Init

After a successful `bmad init`, BMad Master will:
- Confirm workspace creation
- Display the current project state
- Present its workflow menu
- Be ready to start Phase 1 (Product Discovery)

---

## Option C — Developer Symlink Setup (Dev Only)

> [!NOTE]
> **This option is for contributors and framework developers only.** It is NOT recommended for production use. Symlinks are used in the `a0_bmad_method` project's own development (dogfooding) for hot-reloading during framework development.

If you are contributing to BMAD or developing a fork, you can symlink the plugin components into Agent Zero for immediate live testing without copying:

```bash
# From the Agent Zero root
ln -s /path/to/a0_bmad_method /path/to/agent-zero/usr/plugins/bmad
```

Or symlink individual components:

```bash
# Symlink agents and skills into A0 for live testing
for d in /path/to/a0_bmad_method/agents/bmad-*/; do
  ln -s "$d" /path/to/agent-zero/agents/
done
```

> [!WARNING]
> **Dev-only caveat:** End users MUST install by copying (Options A or B). Symlinks create path dependencies that break portability. Never ship or document symlinks as a production install method.

---

## Upgrade Path

When a new version of BMAD Method is released:

| Component | Action | Reason |
|-----------|--------|---------|
| `agents/` | ✅ Overwrite | Agent profiles, prompts, settings updated in releases |
| `skills/` | ✅ Overwrite | Workflow files, module-help.csv updated in releases |
| `extensions/` | ✅ Overwrite | Hook scripts updated in releases |
| `webui/` | ✅ Overwrite | Dashboard UI updated in releases |
| `api/` | ✅ Overwrite | API handlers updated in releases |
| `plugin.yaml` | ✅ Overwrite | Version and manifest updated in releases |
| `.a0proj/` | ⚠️ **Preserve** | All project state: instructions, memory, knowledge, artifacts |

> [!WARNING]
> **Never overwrite `.a0proj/`** — it contains your project state files (`02-bmad-state.md`), FAISS memory stores (`.a0proj/memory/`), knowledge base (`.a0proj/knowledge/`), and all generated artifacts (`.a0proj/_bmad-output/`). Overwriting it destroys project history and agent memory.

### Upgrade Command (Option A — Clone)

```bash
cd /path/to/agent-zero/usr/plugins/bmad
git pull origin main
# .a0proj/ is in .gitignore — it will not be affected
```

### Upgrade Command (Option B — Copy)

```bash
# Backup .a0proj first (optional but recommended)
cp -r /path/to/agent-zero/usr/plugins/bmad/.a0proj /tmp/bmad-a0proj-backup

# Copy new version over old (preserves .a0proj because it's excluded from the repo)
cp -r /path/to/new-bmad_method/. /path/to/agent-zero/usr/plugins/bmad/
```

---

## Troubleshooting

### Plugin not appearing after install

**Symptom:** BMAD Method does not appear in the Agent Zero plugin list.

**Fix:**
1. Confirm the plugin folder is named exactly `bmad` — not `bmad_method`, `a0-bmad-method`, or a repo default name
2. Confirm the folder is inside `usr/plugins/` (e.g. `/a0/usr/plugins/bmad/`)
3. Confirm `plugin.yaml` exists at the plugin root (`/a0/usr/plugins/bmad/plugin.yaml`)
4. Restart Agent Zero fully — plugins are read on startup only

### Wrong folder name

**Symptom:** Dashboard button missing, extension hooks not firing, internal paths broken.

**Fix:** Rename the folder to `bmad`:
```bash
mv /path/to/agent-zero/usr/plugins/bmad_method /path/to/agent-zero/usr/plugins/bmad
```
Then restart Agent Zero.

### `bmad init` failing or producing empty state

**Symptom:** `bmad init` completes but `01-bmad-config.md` or `02-bmad-state.md` are missing or empty.

**Fix:**
1. Confirm you are using the **BMad Master** profile (not a specialist agent)
2. Confirm the `bmad-init` skill is present at `skills/bmad-init/SKILL.md`
3. Check that Agent Zero has write access to the project's `.a0proj/` directory
4. Try running `bmad init` again — it is idempotent

### Dashboard not loading

**Symptom:** The BMAD sidebar button appears but the dashboard shows an error or blank screen.

**Fix:**
1. Confirm `webui/bmad-dashboard.html` and `webui/bmad-dashboard-store.js` exist
2. Confirm `api/_bmad_status.py` exists
3. Confirm `bmad init` has been run — the dashboard reads `02-bmad-state.md` which only exists after init
4. Check Agent Zero logs for API errors

### Agents not recalling project context

**Symptom:** Agent starts fresh each session with no memory of prior decisions.

**Fix:**
1. Confirm the agent has a `plugins/a0_memory/config.json` with the correct `memory_subdir`
2. Confirm `agent_knowledge_subdir` is set in the agent's `settings.json`
3. Confirm `.a0proj/memory/` directory is writable and not empty for active agents
4. Agents with no prior `memory_save` calls have no FAISS store yet — this is normal (lazy seeding)

---

*See [README.md](README.md) for framework overview, agent personas, and skill descriptions.*
