---
name: flowmark
description: Fast, consistent Markdown auto-formatter for typographic cleanup, normalization, and clean semantic line breaks. Use when creating, editing, or cleaning Markdown; formatting LLM-generated docs; adopting Flowmark in a repository; adding Markdown format scripts or commit hooks; or replacing Prettier or another Markdown formatter.
allowed-tools: Bash(flowmark:*), Bash(uvx:*), Read, Write
---
<!-- DO NOT EDIT: `flowmark --install-skill` (format=f03 surface=skill-md) -->

# Flowmark - Markdown Auto-Formatter

Fast, consistent Markdown auto-formatter.
Run it on Markdown you generate or edit so committed diffs stay small and readable.
It is conservative and safe to run on every file: it never modifies code blocks or
inline code.

## Format Markdown

Format in place with all auto-formatting (typography, cleanups, semantic line breaks):

```bash
flowmark --auto FILE   # one file
flowmark --auto .      # whole tree (respects .gitignore and .flowmarkignore)
```

Omit `--auto` to preview to stdout; pipe stdin with `-` (e.g. `cat FILE | flowmark -`).

Use `flowmark` when it is already on `PATH`. Otherwise use the fast
[Rust port](https://github.com/jlevy/flowmark-rs) with a version-pinned `uvx` runner
(never `@latest`):

```bash
uvx --from flowmark-rs==0.3.2 flowmark --auto FILE
```

The [Python reference](https://github.com/jlevy/flowmark) remains available when its
library API or a newer unported patch is required:

```bash
uvx --from flowmark==0.7.3 flowmark --auto FILE
```

## Adopt Flowmark in a Repository

If this skill came from `flowmark --skill`, run the same runner with `--install-skill`
from the project root to materialize the complete bundle.
Then, for a repository-wide migration, Makefile wiring, `.flowmarkignore`, commit hooks,
CI policy, and disabling Prettier or other competing Markdown formatters, read
[project-setup.md](references/project-setup.md) in full before editing.

## Full Documentation

Flowmark documents itself.
Use the CLI rather than reproducing details here:

- `flowmark --help` — every flag: `--semantic`, `--smartquotes`, `--ellipses`,
  `--width`, `--check`, list spacing, and file discovery
  (`--extend-include`/`--extend-exclude`).
- `flowmark --docs` — the full guide: configuration, file discovery, editor setup, the
  Python library API, and installing this skill (`flowmark --install-skill`).

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
