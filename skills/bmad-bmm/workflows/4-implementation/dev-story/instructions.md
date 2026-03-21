> ⚠️ **CRITICAL:** The workflow execution engine is governed by: {project-root}/skills/bmad-init/core/tasks/workflow.xml
> ⚠️ **CRITICAL:** You MUST have already loaded and processed: {installed_path}/workflow.yaml
> ⚠️ **CRITICAL:** Communicate all responses in {communication_language} and language MUST be tailored to {user_skill_level}
> ⚠️ **CRITICAL:** Generate all documents in {document_output_language}
> ⚠️ **CRITICAL:** Only modify the story file in these areas: Tasks/Subtasks checkboxes, Dev Agent Record (Debug Log, Completion Notes), File List,
    Change Log, and Status
> ⚠️ **CRITICAL:** Execute ALL steps in exact order; do NOT skip steps
> ⚠️ **CRITICAL:** Absolutely DO NOT stop because of "milestones", "significant progress", or "session boundaries". Continue in a single execution
    until the story is COMPLETE (all ACs satisfied and all tasks/subtasks checked) UNLESS a HALT condition is triggered or the USER gives
    other instruction.
> ⚠️ **CRITICAL:** Do NOT schedule a "next session" or request review pauses unless a HALT condition applies. Only Step 6 decides completion.
> ⚠️ **CRITICAL:** User skill level ({user_skill_level}) affects conversation style ONLY, not code updates.

## Step 1 — Find next ready story and load it `[sprint-status]`

  **If** *{{story_path}} is provided*:
      - **Action:** Use {{story_path}} directly
      - **Action:** Read COMPLETE story file
      - **Action:** Extract story_key from filename or metadata
      > **Goto** step task_check

  **If** *{{sprint_status}} file exists*:
  > ⚠️ **CRITICAL:** MUST read COMPLETE sprint-status.yaml file from start to end to preserve order
      - **Action:** Load the FULL file: {{sprint_status}}
      - **Action:** Read ALL lines from beginning to end - do not skip any content
      - **Action:** Parse the development_status section completely to understand story order
      - **Action:** Find the FIRST story (by reading in order from top to bottom) where:
        - Key matches pattern: number-number-name (e.g., "1-2-user-auth")
        - NOT an epic key (epic-X) or retrospective (epic-X-retrospective)
        - Status value equals "ready-for-dev"

      **If** *no ready-for-dev or in-progress story found*:

    📋 No ready-for-dev stories found in sprint-status.yaml

          **Current Sprint Status:** {{sprint_status_summary}}

          **What would you like to do?**
          1. Run `create-story` to create next story from epics with comprehensive context
          2. Run `*validate-create-story` to improve existing stories before development (recommended quality check)
          3. Specify a particular story file to develop (provide full path)
          4. Check {{sprint_status}} file to see current sprint status

          💡 **Tip:** Stories in `ready-for-dev` may not have been validated. Consider running `validate-create-story` first for a quality
          check.

          **❓ Ask user:**
          Choose option [1], [2], [3], or [4], or specify story file path:

          **If** *user chooses '1'*:
              - **Action:** HALT - Run create-story to create next story

          **If** *user chooses '2'*:
              - **Action:** HALT - Run validate-create-story to improve existing stories

          **If** *user chooses '3'*:

              **❓ Ask user:**
              Provide the story file path to develop:
              - **Action:** Store user-provided story path as {{story_path}}
              > **Goto** step task_check

          **If** *user chooses '4'*:

      Loading {{sprint_status}} for detailed status review...
              - **Action:** Display detailed sprint status analysis
              - **Action:** HALT - User can review sprint status and provide story path

          **If** *user provides story file path*:
              - **Action:** Store user-provided story path as {{story_path}}
              > **Goto** step task_check

  **If** *{{sprint_status}} file does NOT exist*:
      - **Action:** Search {implementation_artifacts} for stories directly
      - **Action:** Find stories with "ready-for-dev" status in files
      - **Action:** Look for story files matching pattern: *-*-*.md
      - **Action:** Read each candidate story file to check Status section

      **If** *no ready-for-dev stories found in story files*:

    📋 No ready-for-dev stories found

          **Available Options:**
          1. Run `create-story` to create next story from epics with comprehensive context
          2. Run `*validate-create-story` to improve existing stories
          3. Specify which story to develop

          **❓ Ask user:**
          What would you like to do? Choose option [1], [2], or [3]:

          **If** *user chooses '1'*:
              - **Action:** HALT - Run create-story to create next story

          **If** *user chooses '2'*:
              - **Action:** HALT - Run validate-create-story to improve existing stories

          **If** *user chooses '3'*:

              **❓ Ask user:**
              It's unclear what story you want developed. Please provide the full path to the story file:
              - **Action:** Store user-provided story path as {{story_path}}
              - **Action:** Continue with provided story file

      **If** *ready-for-dev story found in files*:
          - **Action:** Use discovered story file and extract story_key
  - **Action:** Store the found story_key (e.g., "1-2-user-authentication") for later status updates
  - **Action:** Find matching story file in {implementation_artifacts} using story_key pattern: {{story_key}}.md
  - **Action:** Read COMPLETE story file from discovered path
  <!-- anchor: task_check -->
  - **Action:** Parse sections: Story, Acceptance Criteria, Tasks/Subtasks, Dev Notes, Dev Agent Record, File List, Change Log, Status
  - **Action:** Load comprehensive context from story file's Dev Notes section
  - **Action:** Extract developer guidance from Dev Notes: architecture requirements, previous learnings, technical specifications
  - **Action:** Use enhanced story context to inform implementation decisions and approaches
  - **Action:** Identify first incomplete task (unchecked [ ]) in Tasks/Subtasks
  - **Action (if** *no incomplete tasks***): 
    - Completion sequence
  - **Action (if** *story file inaccessible***): HALT: "Cannot develop story without access to story file"
  - **Action (if** *incomplete task or subtask requirements ambiguous***): ASK user to clarify or HALT

## Step 2 — Load project context and story information

> ⚠️ **CRITICAL:** Load all available context to inform implementation
  - **Action:** Load {project_context} for coding standards and project-wide patterns (if exists)
  - **Action:** Parse sections: Story, Acceptance Criteria, Tasks/Subtasks, Dev Notes, Dev Agent Record, File List, Change Log, Status
  - **Action:** Load comprehensive context from story file's Dev Notes section
  - **Action:** Extract developer guidance from Dev Notes: architecture requirements, previous learnings, technical specifications
  - **Action:** Use enhanced story context to inform implementation decisions and approaches

✅ **Context Loaded**
      Story and project context available for implementation

## Step 3 — Detect review continuation and extract review context

> ⚠️ **CRITICAL:** Determine if this is a fresh start or continuation after code review
  - **Action:** Check if "Senior Developer Review (AI)" section exists in the story file
  - **Action:** Check if "Review Follow-ups (AI)" subsection exists under Tasks/Subtasks

  **If** *Senior Developer Review section exists*:
      - **Action:** Set review_continuation = true
      - **Action:** Extract from "Senior Developer Review (AI)" section:
        - Review outcome (Approve/Changes Requested/Blocked)
        - Review date
        - Total action items with checkboxes (count checked vs unchecked)
        - Severity breakdown (High/Med/Low counts)
      - **Action:** Count unchecked [ ] review follow-up tasks in "Review Follow-ups (AI)" subsection
      - **Action:** Store list of unchecked review items as {{pending_review_items}}

  ⏯️ **Resuming Story After Code Review** ({{review_date}})

        **Review Outcome:** {{review_outcome}}
        **Action Items:** {{unchecked_review_count}} remaining to address
        **Priorities:** {{high_count}} High, {{med_count}} Medium, {{low_count}} Low

        **Strategy:** Will prioritize review follow-up tasks (marked [AI-Review]) before continuing with regular tasks.

  **If** *Senior Developer Review section does NOT exist*:
      - **Action:** Set review_continuation = false
      - **Action:** Set {{pending_review_items}} = empty

  🚀 **Starting Fresh Implementation**

        Story: {{story_key}}
        Story Status: {{current_status}}
        First incomplete task: {{first_task_description}}

## Step 4 — Mark story in-progress `[sprint-status]`

  **If** *{{sprint_status}} file exists*:
      - **Action:** Load the FULL file: {{sprint_status}}
      - **Action:** Read all development_status entries to find {{story_key}}
      - **Action:** Get current status value for development_status[{{story_key}}]

      **If** *current status == 'ready-for-dev' OR review_continuation == true*:
          - **Action:** Update the story in the sprint status report to = "in-progress"

    🚀 Starting work on story {{story_key}}
          Status updated: ready-for-dev → in-progress

      **If** *current status == 'in-progress'*:

    ⏯️ Resuming work on story {{story_key}}
          Story is already marked in-progress

      **If** *current status is neither ready-for-dev nor in-progress*:

    ⚠️ Unexpected story status: {{current_status}}
          Expected ready-for-dev or in-progress. Continuing anyway...
      - **Action:** Store {{current_sprint_status}} for later use

  **If** *{{sprint_status}} file does NOT exist*:

  ℹ️ No sprint status file exists - story progress will be tracked in story file only
      - **Action:** Set {{current_sprint_status}} = "no-sprint-tracking"

## Step 5 — Implement task following red-green-refactor cycle

> ⚠️ **CRITICAL:** FOLLOW THE STORY FILE TASKS/SUBTASKS SEQUENCE EXACTLY AS WRITTEN - NO DEVIATION
  - **Action:** Review the current task/subtask from the story file - this is your authoritative implementation guide
  - **Action:** Plan implementation following red-green-refactor cycle
  - **Action:** Write FAILING tests first for the task/subtask functionality
  - **Action:** Confirm tests fail before implementation - this validates test correctness
  - **Action:** Implement MINIMAL code to make tests pass
  - **Action:** Run tests to confirm they now pass
  - **Action:** Handle error conditions and edge cases as specified in task/subtask
  - **Action:** Improve code structure while keeping tests green
  - **Action:** Ensure code follows architecture patterns and coding standards from Dev Notes
  - **Action:** Document technical approach and decisions in Dev Agent Record → Implementation Plan
  - **Action (if** *new dependencies required beyond story specifications***): HALT: "Additional dependencies need user approval"
  - **Action (if** *3 consecutive implementation failures occur***): HALT and request guidance
  - **Action (if** *required configuration is missing***): HALT: "Cannot proceed without necessary configuration files"
> ⚠️ **CRITICAL:** NEVER implement anything not mapped to a specific task/subtask in the story file
> ⚠️ **CRITICAL:** NEVER proceed to next task until current task/subtask is complete AND tests pass
> ⚠️ **CRITICAL:** Execute continuously without pausing until all tasks/subtasks are complete or explicit HALT condition
> ⚠️ **CRITICAL:** Do NOT propose to pause for review until Step 9 completion gates are satisfied

## Step 6 — Author comprehensive tests

  - **Action:** Create unit tests for business logic and core functionality introduced/changed by the task
  - **Action:** Add integration tests for component interactions specified in story requirements
  - **Action:** Include end-to-end tests for critical user flows when story requirements demand them
  - **Action:** Cover edge cases and error handling scenarios identified in story Dev Notes

## Step 7 — Run validations and tests

  - **Action:** Determine how to run tests for this repo (infer test framework from project structure)
  - **Action:** Run all existing tests to ensure no regressions
  - **Action:** Run the new tests to verify implementation correctness
  - **Action:** Run linting and code quality checks if configured in project
  - **Action:** Validate implementation meets ALL story acceptance criteria; enforce quantitative thresholds explicitly
  - **Action (if** *regression tests fail***): STOP and fix before continuing - identify breaking changes immediately
  - **Action (if** *new tests fail***): STOP and fix before continuing - ensure implementation correctness

## Step 8 — Validate and mark task complete ONLY when fully done

> ⚠️ **CRITICAL:** NEVER mark a task complete unless ALL conditions are met - NO LYING OR CHEATING
  - **Action:** Verify ALL tests for this task/subtask ACTUALLY EXIST and PASS 100%
  - **Action:** Confirm implementation matches EXACTLY what the task/subtask specifies - no extra features
  - **Action:** Validate that ALL acceptance criteria related to this task are satisfied
  - **Action:** Run full test suite to ensure NO regressions introduced

  **If** *task is review follow-up (has [AI-Review] prefix)*:
      - **Action:** Extract review item details (severity, description, related AC/file)
      - **Action:** Add to resolution tracking list: {{resolved_review_items}}
      - **Action:** Mark task checkbox [x] in "Tasks/Subtasks → Review Follow-ups (AI)" section
      - **Action:** Find matching action item in "Senior Developer Review (AI) → Action Items" section by matching description
      - **Action:** Mark that action item checkbox [x] as resolved
      - **Action:** Add to Dev Agent Record → Completion Notes: "✅ Resolved review finding [{{severity}}]: {{description}}"

  **If** *ALL validation gates pass AND tests ACTUALLY exist and pass*:
      - **Action:** ONLY THEN mark the task (and subtasks) checkbox with [x]
      - **Action:** Update File List section with ALL new, modified, or deleted files (paths relative to repo root)
      - **Action:** Add completion notes to Dev Agent Record summarizing what was ACTUALLY implemented and tested

  **If** *ANY validation fails*:
      - **Action:** DO NOT mark task complete - fix issues first
      - **Action:** HALT if unable to fix validation failures

  **If** *review_continuation == true and {{resolved_review_items}} is not empty*:
      - **Action:** Count total resolved review items in this session
      - **Action:** Add Change Log entry: "Addressed code review findings - {{resolved_count}} items resolved (Date: {{date}})"
  - **Action:** Save the story file
  - **Action:** Determine if more incomplete tasks remain
  - **Action (if** *more tasks remain***): 
    - Next task
  - **Action (if** *no tasks remain***): 
    - Completion

## Step 9 — Story completion and mark for review `[sprint-status]`

  - **Action:** Verify ALL tasks and subtasks are marked [x] (re-scan the story document now)
  - **Action:** Run the full regression suite (do not skip)
  - **Action:** Confirm File List includes every changed file
  - **Action:** Execute enhanced definition-of-done validation
  - **Action:** Update the story Status to: "review"
  - **Action:** Validate definition-of-done checklist with essential requirements:
      - All tasks/subtasks marked complete with [x]
      - Implementation satisfies every Acceptance Criterion
      - Unit tests for core functionality added/updated
      - Integration tests for component interactions added when required
      - End-to-end tests for critical flows added when story demands them
      - All tests pass (no regressions, new tests successful)
      - Code quality checks pass (linting, static analysis if configured)
      - File List includes every new/modified/deleted file (relative paths)
      - Dev Agent Record contains implementation notes
      - Change Log includes summary of changes
      - Only permitted story sections were modified

  **If** *{sprint_status} file exists AND {{current_sprint_status}} != 'no-sprint-tracking'*:
      - **Action:** Load the FULL file: {sprint_status}
      - **Action:** Find development_status key matching {{story_key}}
      - **Action:** Verify current status is "in-progress" (expected previous state)
      - **Action:** Update development_status[{{story_key}}] = "review"
      - **Action:** Save file, preserving ALL comments and structure including STATUS DEFINITIONS

  ✅ Story status updated to "review" in sprint-status.yaml

  **If** *{sprint_status} file does NOT exist OR {{current_sprint_status}} == 'no-sprint-tracking'*:

  ℹ️ Story status updated to "review" in story file (no sprint tracking configured)

  **If** *story key not found in sprint status*:

  ⚠️ Story file updated, but sprint-status update failed: {{story_key}} not found

        Story status is set to "review" in file, but sprint-status.yaml may be out of sync.
  - **Action (if** *any task is incomplete***): HALT - Complete remaining tasks before marking ready for review
  - **Action (if** *regression failures exist***): HALT - Fix regression issues before completing
  - **Action (if** *File List is incomplete***): HALT - Update File List with all changed files
  - **Action (if** *definition-of-done validation fails***): HALT - Address DoD failures before completing

## Step 10 — Completion communication and user support

  - **Action:** Execute the enhanced definition-of-done checklist using the validation framework
  - **Action:** Prepare a concise summary in Dev Agent Record → Completion Notes
  - **Action:** Communicate to {user_name} that story implementation is complete and ready for review
  - **Action:** Summarize key accomplishments: story ID, story key, title, key changes made, tests added, files modified
  - **Action:** Provide the story file path and current status (now "review")
  - **Action:** Based on {user_skill_level}, ask if user needs any explanations about:
      - What was implemented and how it works
      - Why certain technical decisions were made
      - How to test or verify the changes
      - Any patterns, libraries, or approaches used
      - Anything else they'd like clarified

  **If** *user asks for explanations*:
      - **Action:** Provide clear, contextual explanations tailored to {user_skill_level}
      - **Action:** Use examples and references to specific code when helpful
  - **Action:** Once explanations are complete (or user indicates no questions), suggest logical next steps
  - **Action:** Recommended next steps (flexible based on project setup):
      - Review the implemented story and test the changes
      - Verify all acceptance criteria are met
      - Ensure deployment readiness if applicable
      - Run `code-review` workflow for peer review
      - Optional: If Test Architect module installed, run `/bmad:tea:automate` to expand guardrail tests

💡 **Tip:** For best results, run `code-review` using a **different** LLM than the one that implemented this story.

  **If** *{sprint_status} file exists*:
      - **Action:** Suggest checking {sprint_status} to see project progress
  - **Action:** Remain flexible - allow user to choose their own path or ask for other assistance
