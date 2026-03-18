# Shard Document

_Splits large markdown documents into smaller, organized files based on level 2 (default) sections. Use if the user says perform shard document_

**Objective:** Split large markdown documents into smaller, organized files based on level 2 sections using @kayvan/markdown-tree-parser tool

**⚠️ LLM EXECUTION RULES (MANDATORY):**
- MANDATORY: Execute ALL steps in the flow section IN EXACT ORDER
- DO NOT skip steps or change the sequence
- HALT immediately when halt-conditions are met
- Each action xml tag within step xml tag is a REQUIRED action to complete that step
- Sections outside flow (validation, output, critical-context) provide essential context - review and apply throughout execution

**Critical Context:**
- Uses `npx @kayvan/markdown-tree-parser` to automatically shard documents by level 2 headings and generate an index

---

## Step 1 — Get Source Document

  - **Action:** Ask user for the source document path if not provided already
  - **Action:** Verify file exists and is accessible
  - **Action:** Verify file is markdown format (.md extension)
  - **Action (if** *file not found or not markdown***): HALT with error message

## Step 2 — Get Destination Folder

  - **Action:** Determine default destination: same location as source file, folder named after source file without .md extension
  - **Action:** Example: /path/to/architecture.md → /path/to/architecture/
  - **Action:** Ask user for the destination folder path ([y] to confirm use of default: [suggested-path], else enter a new path)
  - **Action (if** *user accepts default***): Use the suggested destination path
  - **Action (if** *user provides custom path***): Use the custom destination path
  - **Action:** Verify destination folder exists or can be created
  - **Action:** Check write permissions for destination
  - **Action (if** *permission denied***): HALT with error message

## Step 3 — Execute Sharding

  - **Action:** Inform user that sharding is beginning
  - **Action:** Execute command: `npx @kayvan/markdown-tree-parser explode [source-document] [destination-folder]`
  - **Action:** Capture command output and any errors
  - **Action (if** *command fails***): HALT and display error to user

## Step 4 — Verify Output

  - **Action:** Check that destination folder contains sharded files
  - **Action:** Verify index.md was created in destination folder
  - **Action:** Count the number of files created
  - **Action (if** *no files created***): HALT with error message

## Step 5 — Report Completion

  - **Action:** Display completion report to user including:
  - - Source document path and name
  - - Destination folder path
  - - Number of section files created
  - - Confirmation that index.md was created
  - - Any tool output or warnings
  - **Action:** Inform user that sharding completed successfully

## Step 6 — Handle Original Document

> ⚠️ **CRITICAL:** Keeping both the original and sharded versions defeats the purpose of sharding and can cause confusion
  - **Action:** Present user with options for the original document:

  **❓ Ask user:**
  What would you like to do with the original document `[source-document-name]`?

        Options:
        [d] Delete - Remove the original (recommended - shards can always be recombined)
        [m] Move to archive - Move original to a backup/archive location
        [k] Keep - Leave original in place (NOT recommended - defeats sharding purpose)

        Your choice (d/m/k):

  **If** *user selects 'd' (delete)*:
      - **Action:** Delete the original source document file
      - **Action:** Confirm deletion to user: "✓ Original document deleted: [source-document-path]"
      > **Note:** The document can be reconstructed from shards by concatenating all section files in order

  **If** *user selects 'm' (move)*:
      - **Action:** Determine default archive location: same directory as source, in an "archive" subfolder
      - **Action:** Example: /path/to/architecture.md → /path/to/archive/architecture.md

      **❓ Ask user:**
      Archive location ([y] to use default: [default-archive-path], or provide custom path):
      - **Action (if** *user accepts default***): Use default archive path
      - **Action (if** *user provides custom path***): Use custom archive path
      - **Action:** Create archive directory if it doesn't exist
      - **Action:** Move original document to archive location
      - **Action:** Confirm move to user: "✓ Original document moved to: [archive-path]"

  **If** *user selects 'k' (keep)*:
      - **Action:** Display warning to user:

  ⚠️ WARNING: Keeping both original and sharded versions is NOT recommended.

          This creates confusion because:
          - The discover_inputs protocol may load the wrong version
          - Updates to one won't reflect in the other
          - You'll have duplicate content taking up space

          Consider deleting or archiving the original document.
      - **Action:** Confirm user choice: "Original document kept at: [source-document-path]"

## Halt Conditions ⚠️

- HALT if npx command fails or produces no output files
