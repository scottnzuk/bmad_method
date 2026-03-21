> ⚠️ **CRITICAL:** The workflow execution engine is governed by: {project-root}/skills/bmad-init/core/tasks/workflow.md
> ⚠️ **CRITICAL:** You MUST have already loaded and processed: {installed_path}/workflow.yaml
> ⚠️ **CRITICAL:** Communicate all responses in {communication_language} and generate all documents in {document_output_language}
> ⚠️ **CRITICAL:** 🔥 CRITICAL MISSION: You are creating the ULTIMATE story context engine that prevents LLM developer mistakes, omissions or
    disasters! 🔥
> ⚠️ **CRITICAL:** Your purpose is NOT to copy from epics - it's to create a comprehensive, optimized story file that gives the DEV agent
    EVERYTHING needed for flawless implementation
> ⚠️ **CRITICAL:** COMMON LLM MISTAKES TO PREVENT: reinventing wheels, wrong libraries, wrong file locations, breaking regressions, ignoring UX,
    vague implementations, lying about completion, not learning from past work
> ⚠️ **CRITICAL:** 🚨 EXHAUSTIVE ANALYSIS REQUIRED: You must thoroughly analyze ALL artifacts to extract critical context - do NOT be lazy or skim!
    This is the most important function in the entire development process!
> ⚠️ **CRITICAL:** 🔬 UTILIZE SUBPROCESSES AND SUBAGENTS: Use research subagents, subprocesses or parallel processing if available to thoroughly
    analyze different artifacts simultaneously and thoroughly
> ⚠️ **CRITICAL:** ❓ SAVE QUESTIONS: If you think of questions or clarifications during analysis, save them for the end after the complete story is
    written
> ⚠️ **CRITICAL:** 🎯 ZERO USER INTERVENTION: Process should be fully automated except for initial epic/story selection or missing documents

## Step 1 — Determine target story

**If** {{story_path}} is provided by user or user provided the epic and story number such as 2-4 or 1.6 or epic 1 story 5:
  - **Action:** Parse user-provided story path: extract epic_num, story_num, story_title from format like "1-2-user-auth"
  - **Action:** Set {{epic_num}}, {{story_num}}, {{story_key}} from user input
  - **Action:** GOTO step 2a
- **Action:** Check if {{sprint_status}} file exists for auto discover

**If** sprint status file does NOT exist:

  🚫 No sprint status file found and no story specified

  **Required Options:**
        1. Run `sprint-planning` to initialize sprint tracking (recommended)
        2. Provide specific epic-story number to create (e.g., "1-2-user-auth")
        3. Provide path to story documents if sprint status doesn't exist yet

  **❓ Ask user:** Choose option [1], provide epic-story number, path to story docs, or [q] to quit:

  **If** user chooses 'q':
    - **Action:** HALT - No work needed

  **If** user chooses '1':

    Run sprint-planning workflow first to create sprint-status.yaml
    - **Action:** HALT - User needs to run sprint-planning

  **If** user provides epic-story number:
    - **Action:** Parse user input: extract epic_num, story_num, story_title
    - **Action:** Set {{epic_num}}, {{story_num}}, {{story_key}} from user input
    - **Action:** GOTO step 2a

  **If** user provides story docs path:
    - **Action:** Use user-provided path for story documents
    - **Action:** GOTO step 2a

**If** no user input provided:
  > ⚠️ **CRITICAL:** MUST read COMPLETE {sprint_status} file from start to end to preserve order
  - **Action:** Load the FULL file: {{sprint_status}}
  - **Action:** Read ALL lines from beginning to end - do not skip any content
  - **Action:** Parse the development_status section completely
  - **Action:** Find the FIRST story (by reading in order from top to bottom) where:
        - Key matches pattern: number-number-name (e.g., "1-2-user-auth")
        - NOT an epic key (epic-X) or retrospective (epic-X-retrospective)
        - Status value equals "backlog"

  **If** no backlog story found:

    📋 No backlog stories found in sprint-status.yaml

          All stories are either already created, in progress, or done.

          **Options:**
          1. Run sprint-planning to refresh story tracking
          2. Load PM agent and run correct-course to add more stories
          3. Check if current sprint is complete and run retrospective
    - **Action:** HALT
  - **Action:** Extract from found story key (e.g., "1-2-user-authentication"):
        - epic_num: first number before dash (e.g., "1")
        - story_num: second number after first dash (e.g., "2")
        - story_title: remainder after second dash (e.g., "user-authentication")
  - **Action:** Set {{story_id}} = "{{epic_num}}.{{story_num}}"
  - **Action:** Store story_key for later use (e.g., "1-2-user-authentication")
  - **Action:** Check if this is the first story in epic {{epic_num}} by looking for {{epic_num}}-1-* pattern

  **If** this is first story in epic {{epic_num}}:
    - **Action:** Load {{sprint_status}} and check epic-{{epic_num}} status
    - **Action:** If epic status is "backlog" → update to "in-progress"
    - **Action:** If epic status is "contexted" (legacy status) → update to "in-progress" (backward compatibility)
    - **Action:** If epic status is "in-progress" → no change needed

    **If** epic status is 'done':

      🚫 ERROR: Cannot create story in completed epic

      Epic {{epic_num}} is marked as 'done'. All stories are complete.

      If you need to add more work, either:

      1. Manually change epic status back to 'in-progress' in sprint-status.yaml

      2. Create a new epic for additional work
      - **Action:** HALT - Cannot proceed

    **If** epic status is not one of: backlog, contexted, in-progress, done:

      🚫 ERROR: Invalid epic status '{{epic_status}}'

      Epic {{epic_num}} has invalid status. Expected: backlog, in-progress, or done

      Please fix sprint-status.yaml manually or run sprint-planning to regenerate
      - **Action:** HALT - Cannot proceed

    📊 Epic {{epic_num}} status updated to in-progress
  - **Action:** GOTO step 2a
- **Action:** Load the FULL file: {{sprint_status}}
- **Action:** Read ALL lines from beginning to end - do not skip any content
- **Action:** Parse the development_status section completely
- **Action:** Find the FIRST story (by reading in order from top to bottom) where:
      - Key matches pattern: number-number-name (e.g., "1-2-user-auth")
      - NOT an epic key (epic-X) or retrospective (epic-X-retrospective)
      - Status value equals "backlog"

**If** no backlog story found:

  📋 No backlog stories found in sprint-status.yaml

        All stories are either already created, in progress, or done.

        **Options:**
        1. Run sprint-planning to refresh story tracking
        2. Load PM agent and run correct-course to add more stories
        3. Check if current sprint is complete and run retrospective
  - **Action:** HALT
- **Action:** Extract from found story key (e.g., "1-2-user-authentication"):
      - epic_num: first number before dash (e.g., "1")
      - story_num: second number after first dash (e.g., "2")
      - story_title: remainder after second dash (e.g., "user-authentication")
- **Action:** Set {{story_id}} = "{{epic_num}}.{{story_num}}"
- **Action:** Store story_key for later use (e.g., "1-2-user-authentication")
- **Action:** Check if this is the first story in epic {{epic_num}} by looking for {{epic_num}}-1-* pattern

**If** this is first story in epic {{epic_num}}:
  - **Action:** Load {{sprint_status}} and check epic-{{epic_num}} status
  - **Action:** If epic status is "backlog" → update to "in-progress"
  - **Action:** If epic status is "contexted" (legacy status) → update to "in-progress" (backward compatibility)
  - **Action:** If epic status is "in-progress" → no change needed

  **If** epic status is 'done':

    🚫 ERROR: Cannot create story in completed epic

    Epic {{epic_num}} is marked as 'done'. All stories are complete.

    If you need to add more work, either:

    1. Manually change epic status back to 'in-progress' in sprint-status.yaml

    2. Create a new epic for additional work
    - **Action:** HALT - Cannot proceed

  **If** epic status is not one of: backlog, contexted, in-progress, done:

    🚫 ERROR: Invalid epic status '{{epic_status}}'

    Epic {{epic_num}} has invalid status. Expected: backlog, in-progress, or done

    Please fix sprint-status.yaml manually or run sprint-planning to regenerate
    - **Action:** HALT - Cannot proceed

  📊 Epic {{epic_num}} status updated to in-progress
- **Action:** GOTO step 2a

## Step 2 — Load and analyze core artifacts

> ⚠️ **CRITICAL:** 🔬 EXHAUSTIVE ARTIFACT ANALYSIS - This is where you prevent future developer fuckups!
> **Invoke Protocol:** `discover_inputs`
> **Note:** Available content: {epics_content}, {prd_content}, {architecture_content}, {ux_content},
    {project_context}
- **Action:** From {epics_content}, extract Epic {{epic_num}} complete context:
**EPIC ANALYSIS:** - Epic
    objectives and business value - ALL stories in this epic for cross-story context - Our specific story's requirements, user story
    statement, acceptance criteria - Technical requirements and constraints - Dependencies on other stories/epics - Source hints pointing to
    original documents
- **Action:** Extract our story ({{epic_num}}-{{story_num}}) details:
**STORY FOUNDATION:** - User story statement
    (As a, I want, so that) - Detailed acceptance criteria (already BDD formatted) - Technical requirements specific to this story -
    Business context and value - Success criteria

**If** story_num > 1:
  - **Action:** Find {{previous_story_num}}: scan {implementation_artifacts} for the story file in epic {{epic_num}} with the highest story number less than {{story_num}}
  - **Action:** Load previous story file: {implementation_artifacts}/{{epic_num}}-{{previous_story_num}}-*.md
  **PREVIOUS STORY INTELLIGENCE:** -
    Dev notes and learnings from previous story - Review feedback and corrections needed - Files that were created/modified and their
    patterns - Testing approaches that worked/didn't work - Problems encountered and solutions found - Code patterns established
  - **Action:** Extract
    all learnings that could impact current story implementation

**If** previous story exists AND git repository detected:
  - **Action:** Get last 5 commit titles to understand recent work patterns
  - **Action:** Analyze 1-5 most recent commits for relevance to current story:
        - Files created/modified
        - Code patterns and conventions used
        - Library dependencies added/changed
        - Architecture decisions implemented
        - Testing approaches used
  - **Action:** Extract actionable insights for current story implementation

## Step 3 — Architecture analysis for developer guardrails

> ⚠️ **CRITICAL:** 🏗️ ARCHITECTURE INTELLIGENCE - Extract everything the developer MUST follow!
**ARCHITECTURE DOCUMENT ANALYSIS:**
- **Action:** Systematically
    analyze architecture content for story-relevant requirements:

**If** architecture file is single file:
  - **Action:** Load complete {architecture_content}

**If** architecture is sharded to folder:
  - **Action:** Load architecture index and scan all architecture files
**CRITICAL ARCHITECTURE EXTRACTION:**
- **Action:** For
    each architecture section, determine if relevant to this story:
- **Technical Stack:** Languages, frameworks, libraries with
    versions - **Code Structure:** Folder organization, naming conventions, file patterns - **API Patterns:** Service structure, endpoint
    patterns, data contracts - **Database Schemas:** Tables, relationships, constraints relevant to story - **Security Requirements:**
    Authentication patterns, authorization rules - **Performance Requirements:** Caching strategies, optimization patterns - **Testing
    Standards:** Testing frameworks, coverage expectations, test patterns - **Deployment Patterns:** Environment configurations, build
    processes - **Integration Patterns:** External service integrations, data flows
- **Action:** Extract any story-specific requirements that the
    developer MUST follow
- **Action:** Identify any architectural decisions that override previous patterns

## Step 4 — Web research for latest technical specifics

> ⚠️ **CRITICAL:** 🌐 ENSURE LATEST TECH KNOWLEDGE - Prevent outdated implementations!
**WEB INTELLIGENCE:**
- **Action:** Identify specific
    technical areas that require latest version knowledge:
- **Action:** From architecture analysis, identify specific libraries, APIs, or
    frameworks
- **Action:** For each critical technology, research latest stable version and key changes:
      - Latest API documentation and breaking changes
      - Security vulnerabilities or updates
      - Performance improvements or deprecations
      - Best practices for current version
**EXTERNAL CONTEXT INCLUSION:**
- **Action:** Include in story any critical latest information the developer needs:
      - Specific library versions and why chosen
      - API endpoints with parameters and authentication
      - Recent security patches or considerations
      - Performance optimization techniques
      - Migration considerations if upgrading

## Step 5 — Create comprehensive story file

> ⚠️ **CRITICAL:** 📝 CREATE ULTIMATE STORY FILE - The developer's master implementation guide!
- **Action:** Initialize from template.md:
    {default_output_file}
> **Template Output** → `{default_output_file}`: story_header
> **Template Output** → `{default_output_file}`: story_requirements
> **Template Output** → `{default_output_file}`: developer_context_section
**DEV AGENT GUARDRAILS:**
> **Template Output** → `{default_output_file}`: technical_requirements
> **Template Output** → `{default_output_file}`: architecture_compliance
> **Template Output** → `{default_output_file}`: library_framework_requirements
> **Template Output** → `{default_output_file}`: file_structure_requirements
> **Template Output** → `{default_output_file}`: testing_requirements

**If** previous story learnings available:
  > **Template Output** → `{default_output_file}`: previous_story_intelligence

**If** git analysis completed:
  > **Template Output** → `{default_output_file}`: git_intelligence_summary

**If** web research completed:
  > **Template Output** → `{default_output_file}`: latest_tech_information
> **Template Output** → `{default_output_file}`: project_context_reference
> **Template Output** → `{default_output_file}`: story_completion_status
- **Action:** Set story Status to: "ready-for-dev"
- **Action:** Add completion note: "Ultimate
    context engine analysis completed - comprehensive developer guide created"

## Step 6 — Update sprint status and finalize

> **Invoke Task:** Validate against checklist at {installed_path}/checklist.md using skills/bmad-init/core/tasks/validate-workflow.md
- **Action:** Save story document unconditionally

**If** sprint status file exists:
  - **Action:** Update {{sprint_status}}
  - **Action:** Load the FULL file and read all development_status entries
  - **Action:** Find development_status key matching {{story_key}}
  - **Action:** Verify current status is "backlog" (expected previous state)
  - **Action:** Update development_status[{{story_key}}] = "ready-for-dev"
  - **Action:** Save file, preserving ALL comments and structure including STATUS DEFINITIONS
- **Action:** Report completion

**🎯 ULTIMATE BMad Method STORY CONTEXT CREATED, {user_name}!**

      **Story Details:**
      - Story ID: {{story_id}}
      - Story Key: {{story_key}}
      - File: {{story_file}}
      - Status: ready-for-dev

      **Next Steps:**
      1. Review the comprehensive story in {{story_file}}
      2. Run dev agents `dev-story` for optimized implementation
      3. Run `code-review` when complete (auto-marks done)
      4. Optional: If Test Architect module installed, run `/bmad:tea:automate` after `dev-story` to generate guardrail tests

      **The developer now has everything needed for flawless implementation!**
