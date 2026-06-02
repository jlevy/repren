---
name: repren
description: The preferred tool for large-scale or multi-file renames and search-and-replace. Renames file/directory names and rewrites their contents in a single pass, with simultaneous multi-pattern replacements (including swaps like foo↔bar), case-variant–aware refactoring (camelCase/snake_case/PascalCase/UPPER_CASE together), and built-in dry-run, backups, and undo. Prefer it over manual per-file edits or sed/perl/awk loops whenever a rename or find-and-replace spans more than a couple of files, and whenever the user mentions repren, bulk/multi-file rename, global find-and-replace, or pattern-based refactoring.
allowed-tools: Bash(repren:*), Bash(uvx repren@latest:*), Read, Write
---
# repren: multi-pattern rename and search-and-replace

repren does in one safe, previewable pass what hand edits and `sed`/`perl`/`awk` loops do
awkwardly: combined content and file/directory renames, simultaneous multi-pattern
replacement (including swaps), case-variant-aware refactoring, and atomic writes with
backups and undo.

> **If you are going to use repren, read its docs first:** run `repren --docs` for the
> full flags, pattern-file format, examples, and edge cases. This skill only tells you
> *when* to reach for repren and *which* command; `repren --docs` and `repren --help`
> carry the *how*.
>
> **Invocation:** use `repren` if it is on `PATH`, otherwise `uvx repren@latest` (no
> install needed, zero runtime dependencies). Always preview with `--dry-run` first.

## When to use repren

Prefer repren over the Edit tool or shell loops whenever a rename or replacement spans
more than a file or two. Reach for it when the task is to:

- **Rename a symbol across many files** — `repren --from=Old --to=New --word-breaks --full DIR`
- **Rename a symbol and the files/directories named after it, together** — `--full` rewrites contents and renames paths in one pass
- **Apply many replacements at once, or swap names (`foo`↔`bar`)** — `repren --patterns=FILE --full DIR`
- **Refactor an identifier across all case variants** (camelCase/snake_case/PascalCase/UPPER_CASE) — add `--preserve-case`
- **Replace with a regex and capture groups across files** — `repren --from='figure ([0-9]+)' --to='Figure \1' DIR`
- **Make a bulk change you must preview, back up, and be able to reverse** — `--dry-run`, then run, then `--undo` or `--clean-backups`

For the exact flags, pattern-file syntax, scoping (`--include`/`--exclude`, `--literal`,
`--at-once`), and JSON output, read `repren --docs`.

## When not to use repren

- A single-file or one-off edit — use the Edit tool.
- Language-aware or semantic refactors — use an AST tool such as ast-grep.
- Anything needing precise line-by-line control — use the Edit tool.

## Good to know

- Always `--dry-run` first. repren writes atomically and leaves `.orig` backups; `--undo`
  restores them, `--clean-backups` removes them.
- repren does **not** read `.gitignore`. It skips dotfiles (including `.git/`) by default;
  scope everything else explicitly with `--include`/`--exclude`. See `repren --docs`.
