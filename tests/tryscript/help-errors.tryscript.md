---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Help and Error Paths

## H1: Top-level help

```console
$ repren --help
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
              [--full] [--renames] [--literal] [-i] [--dotall] [--preserve-case] [-b]
              [--include INCLUDE_PAT] [--exclude EXCLUDE_PAT] [--at-once] [-t]
              [--walk-only] [-n] [-q] [--format {text,json}]
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
              [--install-skill] [--agent-base DIR] [--skill]
              [root_paths ...]

Powerful CLI string replacement and file renaming for agents and humans

positional arguments:
  root_paths            root paths to process

options:
  -h, --help            show usage
  --version             show program's version number and exit
  --docs                show full documentation
  --from FROM_PAT       single replacement: match string
  --to TO_PAT           single replacement: replacement string
  -p, --patterns PAT_FILE
                        file with multiple replacement patterns (see below)
  --full                do file renames and search/replace on file contents
  --renames             do file renames only; do not modify file contents
  --literal             use exact string matching, rather than regular expression
                        matching
  -i, --insensitive     match case-insensitively
  --dotall              match . to newlines
  --preserve-case       do case-preserving magic to transform all case variants (see
                        below)
  -b, --word-breaks     require word breaks (regex \b) around all matches
  --include INCLUDE_PAT
                        file name regex to include (default is .* to include all files)
  --exclude EXCLUDE_PAT
                        file or directory name regex to exclude (default: paths starting
                        with '.')
  --at-once             transform each file's contents at once, instead of line by line
  -t, --parse-only      parse and show patterns only
  --walk-only           like --dry-run, but only walk directories and list files that
                        will be processed (good for confirming your --include and
                        --exclude patterns)
  -n, --dry-run         dry run: just log matches without changing files
  -q, --quiet           quiet mode: suppress all output except errors
  --format {text,json}  output format: 'text' for human-readable (default), 'json' for
                        machine-parseable
  --backup-suffix BACKUP_SUFFIX
                        suffix for backup files (default: .orig)
  --undo                restore original files from backups (requires same patterns as
                        original operation)
  --clean-backups       remove backup files (standalone mode, no patterns needed)
  --install-skill       install Claude Code skill for repren (by default globally to
                        ~/.claude/skills/repren)
  --agent-base DIR      agent config directory for skills (e.g., './.claude' for
                        project, defaults to ~/.claude)
  --skill               print coding agent skill instructions (SKILL.md content)

Run `repren --help` for usage.
Run `repren --docs` for full docs.
? 0
```

## H2: Version output

```console
$ repren --version
[VERSION]
? 0
```

## H3: Docs entry point

```console
$ repren --docs | grep -F 'Powerful CLI string replacement and file renaming for agents and humans'
Powerful CLI string replacement and file renaming for agents and humans
? 0
```

## H4: Skill output

```console
$ repren --skill | head -3
---
name: repren
description: Performs simultaneous multi-pattern search-and-replace, file/directory renaming, and case-preserving refactoring across codebases. Use for bulk refactoring, global find-and-replace, or when user mentions repren, multi-file rename, or pattern-based transformations.
? 0
```

## E1: Missing patterns is an error

```console
$ repren 2>&1
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
              [--full] [--renames] [--literal] [-i] [--dotall] [--preserve-case] [-b]
              [--include INCLUDE_PAT] [--exclude EXCLUDE_PAT] [--at-once] [-t]
              [--walk-only] [-n] [-q] [--format {text,json}]
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
              [--install-skill] [--agent-base DIR] [--skill]
              [root_paths ...]
repren: error: must specify --patterns or both --from and --to

Run `repren --help` for usage.
Run `repren --docs` for full docs.
? 2
```

## E2: Invalid backup suffix is an error

```console
$ repren --backup-suffix bak --from a --to b fixtures/original/humpty-dumpty.txt 2>&1
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
              [--full] [--renames] [--literal] [-i] [--dotall] [--preserve-case] [-b]
              [--include INCLUDE_PAT] [--exclude EXCLUDE_PAT] [--at-once] [-t]
              [--walk-only] [-n] [-q] [--format {text,json}]
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
              [--install-skill] [--agent-base DIR] [--skill]
              [root_paths ...]
repren: error: --backup-suffix must start with '.'

Run `repren --help` for usage.
Run `repren --docs` for full docs.
? 2
```

## E3: `--clean-backups` treats `--undo` as a no-op

```console
$ repren --undo --clean-backups fixtures/original 2>&1
Removed 0 backup file(s)
? 0
```
