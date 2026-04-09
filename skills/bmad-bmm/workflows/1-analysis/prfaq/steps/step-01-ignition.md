# Stage 1: Ignition

**Language:** Use `{communication_language}` for all output.
**Output Language:** Use `{document_output_language}` for documents.
**Output Location:** `{planning_artifacts}`

---

## On Activation

1. Config is already resolved from `workflow.md` initialization. Confirm you have: `project_name`, `planning_artifacts`, `user_name`, `communication_language`, `document_output_language`.

2. **Greet user** as `{user_name}`, speaking in `{communication_language}`. Be warm but efficient — dream builder energy.

3. **Resume detection:** Check if `{planning_artifacts}/prfaq-{project_name}.md` already exists. If it does, read only the first 20 lines to extract the frontmatter `stage` field and offer to resume from the next stage. Do not read the full document. If the user confirms, route directly to that stage's step file.

4. **Mode detection:**
   - `--headless` / `-H`: Produce complete first-draft PRFAQ from provided inputs without interaction. Validate the input schema only (customer, problem, stakes, solution concept present and non-vague) — do not read any referenced files or documents yourself. If required fields are missing or too vague, return an error with specific guidance on what's needed. Fan out artifact analyzer and web researcher subagents in parallel (see Contextual Gathering below) to process all referenced materials, then create the output document at `{planning_artifacts}/prfaq-{project_name}.md` using `{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/assets/prfaq-template.md` and route to `step-02-press-release.md`.
   - Default: Full interactive coaching — the gauntlet.

**Headless input schema:**
- **Required:** customer (specific persona), problem (concrete), stakes (why it matters), solution (concept)
- **Optional:** competitive context, technical constraints, team/org context, target market, existing research

---

## Setting the Tone

**Set the tone immediately.** This isn't a warm, exploratory greeting. Frame it as a challenge — the user is about to stress-test their thinking by writing the press release for a finished product before building anything. Convey that surviving this process means the concept is ready, and failing here saves wasted effort. Be direct and energizing.

Then briefly ground the user on what a PRFAQ actually is — Amazon's Working Backwards method where you write the finished-product press release first, then answer the hardest customer and stakeholder questions. The point is forcing clarity before committing resources.

Then proceed to Stage 1 below.

---

## Stage 1: Ignition

**Goal:** Get the raw concept on the table and immediately establish customer-first thinking. This stage ends when you have enough clarity on the customer, their problem, and the proposed solution to draft a press release headline.

**Customer-first enforcement:**

- If the user leads with a solution ("I want to build X"): redirect to the customer's problem. Don't let them skip the pain.
- If the user leads with a technology ("I want to use AI/blockchain/etc"): challenge harder. Technology is a "how", not a "why" — push them to articulate the human problem. Strip away the buzzword and ask whether anyone still cares.
- If the user leads with a customer problem: dig deeper into specifics — how they cope today, what they've tried, why it hasn't been solved.

When the user gets stuck, offer concrete suggestions based on what they've shared so far. Draft a hypothesis for them to react to rather than repeating the question harder.

**Concept type detection:** Early in the conversation, identify whether this is a commercial product, internal tool, open-source project, or community/nonprofit initiative. Store this as `{concept_type}` — it calibrates FAQ question generation in Stages 3 and 4. Non-commercial concepts don't have "unit economics" or "first 100 customers" — adapt the framing to stakeholder value, adoption paths, and sustainability instead.

**Essentials to capture before progressing:**
- Who is the customer/user? (specific persona, not "everyone")
- What is their problem? (concrete and felt, not abstract)
- Why does this matter to them? (stakes and consequences)
- What's the initial concept for a solution? (even rough)

**Fast-track:** If the user provides all four essentials in their opening message (or via structured input), acknowledge and confirm understanding, then move directly to document creation and Stage 2 without extended discovery.

**Graceful redirect:** If after 2-3 exchanges the user can't articulate a customer or problem, don't force it — suggest the idea may need more exploration first and recommend they invoke the `bmad-brainstorming` skill to develop it further.

**Contextual Gathering:** Once you understand the concept, gather external context before drafting begins.

1. **Ask about inputs:** Ask the user whether they have existing documents, research, brainstorming, or other materials to inform the PRFAQ. Collect paths for subagent scanning — do not read user-provided files yourself; that's the Artifact Analyzer's job.
2. **Fan out subagents in parallel:**
   - **Artifact Analyzer** (`{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/agents/artifact-analyzer.md`) — Scans `{planning_artifacts}` and `{project_knowledge}` for relevant documents, plus any user-provided paths. Receives the product intent summary so it knows what's relevant.
   - **Web Researcher** (`{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/agents/web-researcher.md`) — Searches for competitive landscape, market context, and current industry data relevant to the concept. Receives the product intent summary.
3. **Graceful degradation:** If subagents are unavailable, scan the most relevant 1-2 documents inline and do targeted web searches directly. Never block the workflow.
4. **Merge findings** with what the user shared. Surface anything surprising that enriches or challenges their assumptions before proceeding.

**Create the output document** at `{planning_artifacts}/prfaq-{project_name}.md` using `{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/assets/prfaq-template.md`. Write the frontmatter (populate `inputs` with any source documents used) and any initial content captured during Ignition. This document is the working artifact — update it progressively through all stages.

**Coaching Notes Capture:** Before moving on, append a `<!-- coaching-notes-stage-1 -->` block to the output document: concept type and rationale, initial assumptions challenged, why this direction over alternatives discussed, key subagent findings that shaped the concept framing, and any user context captured that doesn't fit the PRFAQ itself.

---

## Stage Complete

When you have enough to draft a press release headline, update frontmatter: `stepsCompleted: ["step-01-ignition"]`, `stage: 1`, and `updated` timestamp.

Then load and follow: `{project-root}/skills/bmad-bmm/workflows/1-analysis/prfaq/steps/step-02-press-release.md`
