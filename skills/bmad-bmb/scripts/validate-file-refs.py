#!/usr/bin/env python3
"""
validate-file-refs.py — File Reference Validator for BMAD Skills

Scans *.md, *.yaml, *.csv files in a skill directory recursively,
extracts file path references, and verifies each exists on disk.

Usage:
    validate-file-refs.py <skill_dir> [--strict] [--root REPO_ROOT] [--verbose]

Exit codes:
    0   Clean (or issues found but --strict not set)
    1   Broken refs found with --strict enabled
    2   Bad argument (skill_dir not found)
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCAN_EXTENSIONS = {'.md', '.yaml', '.yml', '.csv'}
SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}

# Patterns that signal a ref is a runtime variable — skip it.
# Single-brace {placeholder}, double-brace {{mustache}}, URLs.
_UNRESOLVABLE_RE = re.compile(
    r'\{[^}]+\}'        # {placeholder}
    r'|\{\{[^}]+\}\}'   # {{mustache}}
    r'|https?://'        # URLs
)


def is_resolvable(ref):
    """Return False if ref contains runtime variables or is otherwise unresolvable."""
    if not ref or not ref.strip():
        return False
    # Skip glob patterns (*), template brackets ([...]), fragment identifiers (#)
    if any(c in ref for c in ('*', '[', ']', '#')):
        return False
    return not _UNRESOLVABLE_RE.search(ref)


# ---------------------------------------------------------------------------
# File Scanner
# ---------------------------------------------------------------------------

def get_files(skill_dir):
    """Recursively find all scannable files in skill_dir."""
    files = []
    for path in sorted(skill_dir.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


# ---------------------------------------------------------------------------
# Code Block Stripping (preserve line numbers)
# ---------------------------------------------------------------------------

def strip_code_blocks(content):
    """Replace ``` blocks with blank lines so line numbers are preserved."""
    def blank_block(m):
        return '\n' * m.group(0).count('\n')
    return re.sub(r'```[\s\S]*?```', blank_block, content)


# ---------------------------------------------------------------------------
# Ref Extraction Patterns
# ---------------------------------------------------------------------------

# Markdown link: [text](./path) or [text](../path)
_MD_LINK_RE = re.compile(r'\[[^\]]*\]\((\.{1,2}/[^)]+)\)')

# Backtick relative: `./path.md` or `../path.md`
_MD_BACKTICK_REL_RE = re.compile(r'`(\.{1,2}/[^`]+\.[a-zA-Z]{1,6})`')

# Quoted relative: './path.md' or "../path.md" (using hex escapes to avoid quote mixing)
_SINGLE_Q = '\x27'
_DOUBLE_Q = '\x22'
_MD_QUOTED_REL_RE = re.compile(
    r'[\x27\x22](\.{1,2}/[^\x27\x22]+\.[a-zA-Z]{1,6})[\x27\x22]'
)

# Step metadata fields with relative paths
_STEP_META_RE = re.compile(
    r'(?:thisStepFile|nextStepFile|continueStepFile|skipToStepFile'
    r'|altStepFile|workflowFile|instructions)\s*:\s*[\x27\x22`]?(\.{1,2}/[^\x27\x22`\s\n]+)'
)

# Load directives: Load: `./path`
_LOAD_DIRECTIVE_RE = re.compile(r'[Ll]oad\s*:\s*`(\.{1,2}/[^`]+)`')

# Repo-root-relative paths in backticks: `skills/bmad-xxx/path.ext`
_BACKTICK_SKILL_RE = re.compile(r'`((?:skills|agents|extensions)/[^`]+\.[a-zA-Z]{1,6})`')

# YAML relative values: key: ./path or key: ../path
_YAML_REL_RE = re.compile(r':\s*(\.{1,2}/[^\s,;\x27\x22\n]+\.[a-zA-Z]{1,6})')


def extract_md_refs(filepath, content):
    """
    Extract file refs from markdown content.
    Returns list of (line_number, raw_ref, ref_type).
    """
    refs = []
    stripped = strip_code_blocks(content)
    lines = stripped.split('\n')

    patterns = [
        (_MD_LINK_RE,          'md-link'),
        (_MD_BACKTICK_REL_RE,  'md-backtick-rel'),
        (_MD_QUOTED_REL_RE,    'md-quoted-rel'),
        (_STEP_META_RE,        'step-meta'),
        (_LOAD_DIRECTIVE_RE,   'load-directive'),
        (_BACKTICK_SKILL_RE,   'md-skill-ref'),
    ]

    for lineno, line in enumerate(lines, 1):
        seen_on_line = set()
        for pattern, ref_type in patterns:
            for m in pattern.finditer(line):
                raw = m.group(1).strip()
                if raw in seen_on_line:
                    continue
                if is_resolvable(raw):
                    refs.append((lineno, raw, ref_type))
                    seen_on_line.add(raw)

    return refs


def extract_yaml_refs(filepath, content):
    """Extract relative path refs from YAML content."""
    refs = []
    for lineno, line in enumerate(content.split('\n'), 1):
        stripped_line = line.strip()
        if stripped_line.startswith('#'):
            continue
        for m in _YAML_REL_RE.finditer(line):
            raw = m.group(1).strip()
            if is_resolvable(raw):
                refs.append((lineno, raw, 'yaml-path'))
    return refs


def extract_csv_refs(filepath, content):
    """
    Extract path refs from CSV files.
    Checks the 'args' column (module-help.csv format) for repo-root-relative paths.
    Also checks 'workflow-file' column for upstream compatibility.
    """
    refs = []
    try:
        reader = csv.DictReader(content.splitlines())
        for row_idx, row in enumerate(reader, 2):  # row 1 = header
            for col in ('args', 'workflow-file'):
                val = (row.get(col) or '').strip()
                if not val:
                    continue
                if not is_resolvable(val):
                    continue
                # Must look like a file path (contains a slash or has an extension)
                if not re.search(r'[/\\]', val) and not re.search(r'\.[a-zA-Z]{1,6}$', val):
                    continue  # Skip bare action identifiers
                refs.append((row_idx, val, 'csv-' + col))
    except Exception:
        pass  # Malformed CSV — skip
    return refs


# ---------------------------------------------------------------------------
# Ref Resolution
# ---------------------------------------------------------------------------

def resolve_ref(raw, source_file, repo_root):
    """
    Resolve a raw ref string to an absolute Path.
    - Relative refs (./... or ../...) resolved against source file dir
    - Repo-root refs (skills/agents/extensions/...) resolved against repo_root
    Returns None if ref type is not recognised.
    """
    if raw.startswith('./') or raw.startswith('../'):
        return (source_file.parent / raw).resolve()
    if re.match(r'^(?:skills|agents|extensions)/', raw):
        return (repo_root / raw).resolve()
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Validate file references in a BMAD skill directory.'
    )
    parser.add_argument('skill_dir', help='Path to the skill directory to scan')
    parser.add_argument('--strict', action='store_true',
                        help='Exit code 1 if any broken references found')
    parser.add_argument('--root', default=None,
                        help='Repo root directory (default: 2 levels above skill_dir)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show all checked references, not just broken ones')
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.exists():
        print('ERROR: skill_dir not found: ' + str(skill_dir), file=sys.stderr)
        sys.exit(2)

    # Repo root: 2 levels above skill_dir (repo_root/skills/bmad-xxx/)
    repo_root = Path(args.root).resolve() if args.root else skill_dir.parents[1]

    print('')
    print('Validating file references in: ' + str(skill_dir))
    print('Repo root:                     ' + str(repo_root))
    mode_str = 'STRICT (exit 1 on issues)' if args.strict else 'WARNING (exit 0)'
    print('Mode:                          ' + mode_str)
    print('')

    files = get_files(skill_dir)
    print('Found ' + str(len(files)) + ' files to scan')
    print('')

    total_refs = 0
    broken_count = 0
    files_with_issues = 0

    for filepath in files:
        try:
            content = filepath.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print('  [READ-ERROR] ' + str(filepath) + ': ' + str(e))
            continue

        ext = filepath.suffix.lower()
        if ext in ('.yaml', '.yml'):
            raw_refs = extract_yaml_refs(filepath, content)
        elif ext == '.csv':
            raw_refs = extract_csv_refs(filepath, content)
        else:
            raw_refs = extract_md_refs(filepath, content)

        broken = []
        ok = []

        for lineno, raw, ref_type in raw_refs:
            total_refs += 1
            resolved = resolve_ref(raw, filepath, repo_root)
            if resolved is None:
                continue  # unrecognised ref type — skip
            if resolved.exists():
                ok.append((lineno, raw, ref_type))
            else:
                try:
                    rel_resolved = resolved.relative_to(repo_root)
                except ValueError:
                    rel_resolved = resolved
                broken.append((lineno, raw, ref_type, str(rel_resolved)))
                broken_count += 1

        try:
            rel_file = filepath.relative_to(repo_root)
        except ValueError:
            rel_file = filepath

        if broken:
            files_with_issues += 1
            print(str(rel_file))
            for lineno, raw, ref_type, resolved_str in broken:
                print('  ' + str(rel_file) + ':' + str(lineno) + ': broken ref -> ' + raw)
                print('    Resolved to: ' + resolved_str)
            print('')
        elif args.verbose and ok:
            print(str(rel_file))
            for lineno, raw, ref_type in ok:
                print('  [OK] line ' + str(lineno) + ' (' + ref_type + '): ' + raw)
            print('')

    print('-' * 60)
    print('')
    print('Summary:')
    print('  Files scanned:       ' + str(len(files)))
    print('  References checked:  ' + str(total_refs))
    print('  Broken references:   ' + str(broken_count))

    if broken_count > 0:
        print('')
        print('  ' + str(files_with_issues) + ' file(s) with broken references')
        if args.strict:
            print('')
            print('  [STRICT MODE] Exiting with failure.')
        else:
            print('')
            print('  Run with --strict to treat broken refs as errors.')
    else:
        print('')
        print('  All file references valid!')

    print('')
    sys.exit(1 if (broken_count > 0 and args.strict) else 0)


if __name__ == '__main__':
    main()
