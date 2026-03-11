"""
BmadSidecarInject — Silently inject sidecar knowledge into system prompt extras.

Runs in message_loop_prompts_after — injects into extras_persistent which renders
silently into the [EXTRAS] section of the system prompt. No visible UI messages.

Fires once per conversation (extras_persistent persists across turns).
"""

import yaml
from pathlib import Path
from helpers.extension import Extension
from agent import LoopData

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]  # from message_loop_prompts_after/

EXTRAS_KEY = "bmad_sidecar"


def _get_plugin_version() -> str:
    """Load plugin version from plugin.yaml."""
    try:
        plugin_yaml = _PLUGIN_ROOT / "plugin.yaml"
        if plugin_yaml.exists():
            data = yaml.safe_load(plugin_yaml.read_text(encoding="utf-8"))
            return data.get("version", "0.0.0")
    except Exception:
        pass
    return "0.0.0"


def _resolve_project_id(agent) -> str:
    """Resolve the active project ID from agent context."""
    try:
        from helpers import projects
        project_name = projects.get_context_project_name(agent.context)
        if project_name:
            return project_name
    except Exception:
        pass
    return "default"


class BmadSidecarInject(Extension):
    """
    Silently inject sidecar knowledge for BMAD agents.
    
    Runs in message_loop_prompts_after — injects into extras_persistent which
    renders silently into the [EXTRAS] section of the system prompt.
    
    Fires once per conversation (extras_persistent persists across turns).
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent:
            return

        # Only for bmad-* profiles
        profile = getattr(self.agent.config, "profile", None) or ""
        if not str(profile).startswith("bmad-"):
            return

        profile_name = str(profile)

        # Already injected this conversation — skip (extras_persistent persists)
        if EXTRAS_KEY in loop_data.extras_persistent:
            return

        # Discover knowledge files from all enabled plugins
        try:
            from helpers import plugins
            knowledge_dirs = plugins.get_enabled_plugin_paths(
                self.agent, "knowledge", profile_name
            )
        except Exception:
            knowledge_dirs = []

        # Read all markdown files
        sections = []
        for kdir in knowledge_dirs:
            kpath = Path(kdir)
            if kpath.exists() and kpath.is_dir():
                for md_file in sorted(kpath.glob("*.md")):
                    try:
                        content = md_file.read_text(encoding="utf-8").strip()
                        if content:
                            sections.append(content)
                    except Exception:
                        continue

        if not sections:
            return

        # Get plugin version
        version = _get_plugin_version()
        src_tag = f"bmad-plugin-{version}"

        # Resolve project ID
        project_id = _resolve_project_id(self.agent)
        project_tag = f"[PROJECT:{project_id}]"
        agent_tag = f"[AGENT:{profile_name}]"

        # Build the injected prompt block
        joined = "\n\n---\n\n".join(sections)

        anchor_block = f"""## 📁 KNOWLEDGE ANCHOR — {profile_name} (constitutional — authoritative)

{joined}

---

## 🧠 Memory Protocol for This Session
Schema: {agent_tag} [CAT:x] {project_tag} [SRC:{src_tag}] [SEEDED/LEARNED]

Your memory store is already isolated to this agent and project — no filter or agent/project tags needed in queries.

To load memories, use the **memory_load** tool with a semantic query describing what you need to recall (e.g. "prior decisions", "user preferences", "architecture choices"). Use threshold 0.7, limit 10.

To save decisions, use the **memory_save** tool with text formatted as:
{agent_tag} [CAT:decisions] {project_tag} [LEARNED]
Decision: ...

Categories for [CAT:x]: `preferences`, `decisions`, `session`

Lazy Seeding: If no [SEEDED] tag found in loaded memories, save each knowledge section above using the memory_save tool with [SRC:{src_tag}] [SEEDED] in the text.

Do NOT use the filter argument. Do NOT write pseudo-code like memory_load(...) or memory_save(...) — always use proper tool calls."""

        # Inject SILENTLY into extras_persistent — renders in [EXTRAS] system prompt section
        loop_data.extras_persistent[EXTRAS_KEY] = anchor_block
