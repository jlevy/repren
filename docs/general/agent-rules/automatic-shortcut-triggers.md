---
description: Automatic Shortcut Triggers
globs:
alwaysApply: true
---
# Automatic Shortcut Triggers

Before responding to ANY coding or development request, you MUST check if a shortcut
applies. If a shortcut applies, you MUST use it.

## Mandatory Check Protocol

1. Scan shortcuts in @docs/general/agent-shortcuts/ for applicable workflows

2. If a shortcut matches → Announce: “Using [shortcut name]”

3. Follow the shortcut exactly

## Shortcut Trigger Table

You can search for all filenames in this table, then read the contents and follow the
instructions.

### Spec Creation and Management

| If user request involves... | Use shortcut |
| --- | --- |
| Creating a new feature plan | @shortcut-new-plan-spec.md |
| Creating an implementation spec | @shortcut-new-implementation-spec.md |
| Creating a validation/test spec | @shortcut-new-validation-spec.md |
| Refining or clarifying an existing spec | @shortcut-refine-spec.md |
| Updating a spec with new information | @shortcut-update-spec.md |
| Updating specs progress and beads | @shortcut-update-specs-status.md |

### Implementation

| If user request involves... | Use shortcut |
| --- | --- |
| Creating implementation beads from a spec | @shortcut-new-implementation-beads-from-spec.md |
| Implementing beads | @shortcut-implement-beads.md |
| Implementing a spec (legacy, no beads) | @shortcut-implement-spec.md |
| Exploratory coding / prototype / spike | @shortcut-coding-spike.md |

### Commits and PRs

| If user request involves... | Use shortcut |
| --- | --- |
| Committing code | @shortcut-precommit-process.md → @shortcut-commit-code.md |
| Creating a validation plan | @shortcut-create-or-update-validation-plan.md |
| Creating a PR with validation | @shortcut-create-or-update-pr-with-validation-plan.md |
| Creating a PR (simple, no validation plan) | @shortcut-create-pr-simple.md |

### Code Review

| If user request involves... | Use shortcut |
| --- | --- |
| Reviewing code, specs, docs | @shortcut-review-all-code-specs-docs-convex.md |
| Reviewing a PR and commenting | @shortcut-review-pr.md |
| Reviewing and fixing a PR with beads | @shortcut-review-pr-and-fix-with-beads.md |

### Research and Architecture

| If user request involves... | Use shortcut |
| --- | --- |
| Research or technical investigation | @shortcut-new-research-brief.md |
| Creating architecture documentation | @shortcut-new-architecture-doc.md |
| Updating/revising architecture docs | @shortcut-revise-architecture-doc.md |

### Cleanup and Maintenance

| If user request involves... | Use shortcut |
| --- | --- |
| Code cleanup or refactoring | @shortcut-cleanup-all.md |
| Removing trivial tests | @shortcut-cleanup-remove-trivial-tests.md |
| Updating docstrings | @shortcut-cleanup-update-docstrings.md |
| Merging from upstream | @shortcut-merge-upstream.md |

## Common Shortcut Chains (Combos)

Some workflows require multiple shortcuts in sequence.
Always complete the full chain when applicable.

### Implement This Spec (Full Feature Flow)

When user says “implement this spec” or similar:

1. @shortcut-new-implementation-beads-from-spec.md — Create beads from the spec

2. @shortcut-implement-beads.md — Implement all beads

3. @shortcut-create-or-update-pr-with-validation-plan.md — Create PR with validation

### Commit Flow

1. @shortcut-precommit-process.md — Run pre-commit checks

2. @shortcut-commit-code.md — Commit changes

### PR Flow (with Validation)

1. @shortcut-precommit-process.md — Run pre-commit checks

2. @shortcut-create-or-update-validation-plan.md — Create/update validation plan

3. @shortcut-create-or-update-pr-with-validation-plan.md — Create/update PR

### New Feature (Full Lifecycle)

1. @shortcut-new-plan-spec.md — Create plan spec

2. @shortcut-new-implementation-beads-from-spec.md — Create implementation beads

3. @shortcut-implement-beads.md — Implement beads

4. @shortcut-create-or-update-pr-with-validation-plan.md — Create PR with validation

## This is NOT Optional

If a shortcut exists for your task, you must use it.
Do not rationalize skipping it.
Common rationalizations to avoid:

- “This is simple, I don’t need a shortcut” → WRONG. Use the shortcut.

- “I know how to do this” → WRONG. The shortcut may have steps you’ll forget.

- “The user didn’t ask for a shortcut” → WRONG. Shortcuts are mandatory when applicable.

- “The shortcut is overkill” → WRONG. Shortcuts ensure consistency and quality.
