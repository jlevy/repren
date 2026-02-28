---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Help and Error Paths

## H1: Top-level help

```console
$ repren --help | grep -F "Powerful CLI string replacement and file renaming for agents and humans"
Powerful CLI string replacement and file renaming for agents and humans
? 0
```

```console
$ repren --help | grep -Fx "  --full                do file renames and search/replace on file contents"
  --full                do file renames and search/replace on file contents
? 0
```

```console
$ repren --help | grep -Fx "  --renames             do file renames only; do not modify file contents"
  --renames             do file renames only; do not modify file contents
? 0
```

```console
$ repren --help | grep -Fx "  -i, --insensitive     match case-insensitively"
  -i, --insensitive     match case-insensitively
? 0
```

```console
$ repren --help | grep -Fx "  --format {text,json}  output format: 'text' for human-readable (default), 'json' for"
  --format {text,json}  output format: 'text' for human-readable (default), 'json' for
? 0
```

```console
$ repren --help | grep -F -- "--clean-backups"
              [--backup-suffix BACKUP_SUFFIX] [--undo] [--clean-backups]
  --clean-backups       remove backup files (standalone mode, no patterns needed)
? 0
```

```console
$ repren --help | grep -F "Run \`repren --docs\` for full docs."
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
