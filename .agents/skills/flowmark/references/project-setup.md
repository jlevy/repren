<!-- DO NOT EDIT: `flowmark --install-skill` (format=f03 surface=skill-reference) -->

# Project Setup and Migration

Use this workflow when adopting Flowmark across a repository.
Keep one `flowmark` skill; project setup is a use case of that skill, not a separate
skill.

## Migration Checklist

1. Find the Markdown sources and identify generated, vendored, fixture, and golden files
   that must retain byte-exact content.
2. Add those paths to `.flowmarkignore`.
3. Make Flowmark the only formatter that owns Markdown.
   Disable Markdown in Prettier, Biome, dprint, editor format-on-save settings, and
   existing Markdown hooks.
4. Add one pinned project command and run it once over the repository.
   Review and commit the baseline reformat separately from content changes.
5. Add an auto-fixing commit hook.
   Prefer a hook that stages its fixes so formatting does not become a manual gate.
6. Do not fail the main build only for ordinary Markdown formatting drift.
   Keep formatting local and automatic; reserve CI drift checks for generated or
   contractually byte-exact documentation.

## Pinned Project Command

Prefer the Rust port through `uvx`:

```makefile
FLOWMARK := uvx --from flowmark-rs==0.3.2 flowmark

.PHONY: format-docs
format-docs:
	$(FLOWMARK) --auto .
```

Passing `.` lets Flowmark discover files once and honor `.gitignore` and
`.flowmarkignore` from the repository root.
Avoid shell `find` pipelines or per-directory invocations unless the repository requires
them.

Start `.flowmarkignore` with content Flowmark must not rewrite:

```gitignore
# Generated or vendored Markdown
docs/api/_generated/
third_party/

# Byte-exact fixtures and golden files
tests/fixtures/
tests/golden/
```

When documentation is generated, format canonical sources first, then regenerate their
mirrors. Exclude generated mirrors from Flowmark so there is one source of truth.

## Auto-Fix on Commit

Lefthook can format and stage Markdown without turning style into a separate failure:

```yaml
pre-commit:
  commands:
    flowmark:
      glob: "*.{md,mdc,markdown}"
      run: uvx --from flowmark-rs==0.3.2 flowmark --auto --force-exclude {staged_files}
      stage_fixed: true
```

`--force-exclude` applies `.flowmarkignore` even though the hook passes explicit file
paths. If generated docs must be refreshed after formatting, call one repository script
or Make target that performs both operations in the required order.

For the `pre-commit` framework, use a local system hook with the same pinned command:

```yaml
repos:
  - repo: local
    hooks:
      - id: flowmark
        name: flowmark
        entry: uvx --from flowmark-rs==0.3.2 flowmark --auto --force-exclude
        language: system
        files: '\.(md|mdc|markdown)$'
```

Keep both hook selectors aligned with any Markdown extensions the repository discovers
through `--extend-include`. The `pre-commit` framework stops the first commit after
modifying files; stage the fixes and retry.
Use Lefthook with `stage_fixed: true` when transparent auto-staging is preferred.

## Disable Competing Markdown Formatters

For Prettier, exclude Markdown in `.prettierignore`:

```gitignore
*.md
```

Also remove Markdown-specific Prettier hooks and editor defaults.
If Flowmark owns MDX or another extension via `--extend-include`, exclude that extension
from Prettier too.

Apply the same ownership rule to other tools: keep them for code and data formats, but
remove Markdown from their include globs and format-on-save configuration.
Do not run two Markdown formatters sequentially; they can churn each other’s output and
make hooks or CI nondeterministic.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
