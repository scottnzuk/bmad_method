> ⚠️ **CRITICAL:** The workflow execution engine is governed by: {project-root}/_bmad/core/tasks/workflow.md
> ⚠️ **CRITICAL:** You MUST have already loaded and processed: {installed_path}/workflow.yaml
> ⚠️ **CRITICAL:** Communicate all responses in {communication_language} and language MUST be tailored to {user_skill_level}
> ⚠️ **CRITICAL:** Generate all documents in {document_output_language}
> ⚠️ **CRITICAL:** 🔥 YOU ARE AN ADVERSARIAL CODE REVIEWER - Find what's wrong or missing! 🔥
> ⚠️ **CRITICAL:** Your purpose: Validate story file claims against actual implementation
> ⚠️ **CRITICAL:** Challenge everything: Are tasks marked [x] actually done? Are ACs really implemented?
> ⚠️ **CRITICAL:** Find 3-10 specific issues in every review minimum - no lazy "looks good" reviews - YOU are so much better than the dev agent
    that wrote this slop
> ⚠️ **CRITICAL:** Read EVERY file in the File List - verify implementation against story requirements
> ⚠️ **CRITICAL:** Tasks marked complete but not done = CRITICAL finding
> ⚠️ **CRITICAL:** Acceptance Criteria not implemented = HIGH severity finding
> ⚠️ **CRITICAL:** Do not review files that are not part of the application's source code. Always exclude the _bmad/ and _bmad-output/ folders from the review. Always exclude IDE and CLI configuration folders like .cursor/ and .windsurf/ and .claude/

## Step 1 — Load story and discover changes

- **Action:** Use provided {{story_path}} or ask user which story file to review
- **Action:** Read COMPLETE story file
- **Action:** Set {{story_key}} = extracted key from filename (e.g., "1-2-user-authentication.md" → "1-2-user-authentication") or story
      metadata
- **Action:** Parse sections: Story, Acceptance Criteria, Tasks/Subtasks, Dev Agent Record → File List, Change Log
- **Action:** Check if git repository detected in current directory

**If** git repository exists:
  - **Action:** Run `git status --porcelain` to find uncommitted changes
  - **Action:** Run `git diff --name-only` to see modified files
  - **Action:** Run `git diff --cached --name-only` to see staged files
  - **Action:** Compile list of actually changed files from git output
- **Action:** Compare story's Dev Agent Record → File List with actual git changes
- **Action:** Note discrepancies:
      - Files in git but not in story File List
      - Files in story File List but no git changes
      - Missing documentation of what was actually changed
> **Invoke Protocol:** `discover_inputs`
- **Action:** Load {project_context} for coding standards (if exists)

## Step 2 — Build review attack plan

- **Action:** Extract ALL Acceptance Criteria from story
- **Action:** Extract ALL Tasks/Subtasks with completion status ([x] vs [ ])
- **Action:** From Dev Agent Record → File List, compile list of claimed changes
- **Action:** Create review plan:
      1. **AC Validation**: Verify each AC is actually implemented
      2. **Task Audit**: Verify each [x] task is really done
      3. **Code Quality**: Security, performance, maintainability
      4. **Test Quality**: Real tests vs placeholder bullshit

## Step 3 — Execute adversarial review

> ⚠️ **CRITICAL:** VALIDATE EVERY CLAIM - Check git reality vs story claims
- **Action:** Review git vs story File List discrepancies:
      1. **Files changed but not in story File List** → MEDIUM finding (incomplete documentation)
      2. **Story lists files but no git changes** → HIGH finding (false claims)
      3. **Uncommitted changes not documented** → MEDIUM finding (transparency issue)
- **Action:** Create comprehensive review file list from story File List and git changes
- **Action:** For EACH Acceptance Criterion:
      1. Read the AC requirement
      2. Search implementation files for evidence
      3. Determine: IMPLEMENTED, PARTIAL, or MISSING
      4. If MISSING/PARTIAL → HIGH SEVERITY finding
- **Action:** For EACH task marked [x]:
      1. Read the task description
      2. Search files for evidence it was actually done
      3. **CRITICAL**: If marked [x] but NOT DONE → CRITICAL finding
      4. Record specific proof (file:line)
- **Action:** For EACH file in comprehensive review list:
      1. **Security**: Look for injection risks, missing validation, auth issues
      2. **Performance**: N+1 queries, inefficient loops, missing caching
      3. **Error Handling**: Missing try/catch, poor error messages
      4. **Code Quality**: Complex functions, magic numbers, poor naming
      5. **Test Quality**: Are tests real assertions or placeholders?

**If** total_issues_found lt 3:
  > ⚠️ **CRITICAL:** NOT LOOKING HARD ENOUGH - Find more problems!
  - **Action:** Re-examine code for:
        - Edge cases and null handling
        - Architecture violations
        - Documentation gaps
        - Integration issues
        - Dependency problems
        - Git commit message quality (if applicable)
  - **Action:** Find at least 3 more specific, actionable issues

## Step 4 — Present findings and fix them

- **Action:** Categorize findings: HIGH (must fix), MEDIUM (should fix), LOW (nice to fix)
- **Action:** Set {{fixed_count}} = 0
- **Action:** Set {{action_count}} = 0

**🔥 CODE REVIEW FINDINGS, {user_name}!**

      **Story:** {{story_file}}
      **Git vs Story Discrepancies:** {{git_discrepancy_count}} found
      **Issues Found:** {{high_count}} High, {{medium_count}} Medium, {{low_count}} Low

      ## 🔴 CRITICAL ISSUES
      - Tasks marked [x] but not actually implemented
      - Acceptance Criteria not implemented
      - Story claims files changed but no git evidence
      - Security vulnerabilities

      ## 🟡 MEDIUM ISSUES
      - Files changed but not documented in story File List
      - Uncommitted changes not tracked
      - Performance problems
      - Poor test coverage/quality
      - Code maintainability issues

      ## 🟢 LOW ISSUES
      - Code style improvements
      - Documentation gaps
      - Git commit message quality

**❓ Ask user:** What should I do with these issues?

      1. **Fix them automatically** - I'll update the code and tests
      2. **Create action items** - Add to story Tasks/Subtasks for later
      3. **Show me details** - Deep dive into specific issues

      Choose [1], [2], or specify which issue to examine:

**If** user chooses 1:
  - **Action:** Fix all HIGH and MEDIUM issues in the code
  - **Action:** Add/update tests as needed
  - **Action:** Update File List in story if files changed
  - **Action:** Update story Dev Agent Record with fixes applied
  - **Action:** Set {{fixed_count}} = number of HIGH and MEDIUM issues fixed
  - **Action:** Set {{action_count}} = 0

**If** user chooses 2:
  - **Action:** Add "Review Follow-ups (AI)" subsection to Tasks/Subtasks
  - **Action:** For each issue: `- [ ] [AI-Review][Severity] Description [file:line]`
  - **Action:** Set {{action_count}} = number of action items created
  - **Action:** Set {{fixed_count}} = 0

**If** user chooses 3:
  - **Action:** Show detailed explanation with code examples
  - **Action:** Return to fix decision

## Step 5 — Update story status and sync sprint tracking

**If** all HIGH and MEDIUM issues fixed AND all ACs implemented:
  - **Action:** Set {{new_status}} = "done"
  - **Action:** Update story Status field to "done"

**If** HIGH or MEDIUM issues remain OR ACs not fully implemented:
  - **Action:** Set {{new_status}} = "in-progress"
  - **Action:** Update story Status field to "in-progress"
- **Action:** Save story file

**If** {sprint_status} file exists:
  - **Action:** Set {{current_sprint_status}} = "enabled"

**If** {sprint_status} file does NOT exist:
  - **Action:** Set {{current_sprint_status}} = "no-sprint-tracking"

**If** {{current_sprint_status}} != 'no-sprint-tracking':
  - **Action:** Load the FULL file: {sprint_status}
  - **Action:** Find development_status key matching {{story_key}}

  **If** {{new_status}} == 'done':
    - **Action:** Update development_status[{{story_key}}] = "done"
    - **Action:** Save file, preserving ALL comments and structure

    ✅ Sprint status synced: {{story_key}} → done

  **If** {{new_status}} == 'in-progress':
    - **Action:** Update development_status[{{story_key}}] = "in-progress"
    - **Action:** Save file, preserving ALL comments and structure

    🔄 Sprint status synced: {{story_key}} → in-progress

  **If** story key not found in sprint status:

    ⚠️ Story file updated, but sprint-status sync failed: {{story_key}} not found in sprint-status.yaml

**If** {{current_sprint_status}} == 'no-sprint-tracking':

  ℹ️ Story status updated (no sprint tracking configured)

**✅ Review Complete!**

      **Story Status:** {{new_status}}
      **Issues Fixed:** {{fixed_count}}
      **Action Items Created:** {{action_count}}

      {{#if new_status == "done"}}Code review complete!{{else}}Address the action items and continue development.{{/if}}
