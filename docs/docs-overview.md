# Human and Agent Development Docs

This folder holds docs and rules for use by humans and LLMs/agents.

Any filenames like @docs/general/agent-rules/python-rules.md are paths from the root of
this repository.

## Documentation Layout

All project and development documentation is organized in `docs/`, which follow the
Speculate project structure:

### `docs/development.md` — Essential development docs

- `development.md` — Environment setup and basic developer workflows (building,
  formatting, linting, testing, committing, etc.)

Always read `development.md` first!
Other docs give background but it includes essential project developer docs.

### `docs/general/` — Cross-project rules and templates

General rules that apply to all projects:

- @docs/general/agent-rules/ — General rules for development best practices (general,
  pre-commit, TypeScript, Convex)

- @docs/general/agent-shortcuts/ — Reusable task prompts for agents

- @docs/general/agent-guidelines/ — Guidelines and notes on development practices

- @docs/general/agent-setup/ — Setup guides for tools (GitHub CLI, beads, etc.)

### `docs/project/` — Project-specific documentation

Project-specific specifications, architecture, and research docs:

- @docs/project/specs/ — Change specifications for features and bugfixes:

  - `active/` — Currently in-progress specifications

  - `done/` — Completed specifications (historic)

  - `future/` — Planned specifications

  - `paused/` — Temporarily paused specifications

- @docs/project/architecture/ — System design references and long-lived architecture
  docs (templates and output go here)

- @docs/project/research/ — Research notes and technical investigations
