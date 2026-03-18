# Index Docs

_Generates or updates an index.md to reference all docs in the folder. Use if user requests to create or update an index of all files in a specific folder_

**⚠️ LLM EXECUTION RULES (MANDATORY):**
- MANDATORY: Execute ALL steps in the flow section IN EXACT ORDER
- DO NOT skip steps or change the sequence
- HALT immediately when halt-conditions are met
- Each action xml tag within step xml tag is a REQUIRED action to complete that step
- Sections outside flow (validation, output, critical-context) provide essential context - review and apply throughout execution

---

## Step 1 — Scan Directory

- List all files and subdirectories in the target location

## Step 2 — Group Content

- Organize files by type, purpose, or subdirectory

## Step 3 — Generate Descriptions

- Read each file to understand its actual purpose and create brief (3-10 word) descriptions based on the content, not just the
        filename

## Step 4 — Create/Update Index

- Write or update index.md with organized file listings

## Output Format

**Example:**
~~~
# Directory Index

      ## Files

      - **[filename.ext](./filename.ext)** - Brief description
      - **[another-file.ext](./another-file.ext)** - Brief description

      ## Subdirectories

      ### subfolder/

      - **[file1.ext](./subfolder/file1.ext)** - Brief description
      - **[file2.ext](./subfolder/file2.ext)** - Brief description

      ### another-folder/

      - **[file3.ext](./another-folder/file3.ext)** - Brief description
~~~

## Halt Conditions  ⚠️

- HALT if target directory does not exist or is inaccessible
- HALT if user does not have write permissions to create index.md

## Validation Rules

- Use relative paths starting with ./
- Group similar files together
- Read file contents to generate accurate descriptions - don't guess from filenames
- Keep descriptions concise but informative (3-10 words)
- Sort alphabetically within groups
- Skip hidden files (starting with .) unless specified
