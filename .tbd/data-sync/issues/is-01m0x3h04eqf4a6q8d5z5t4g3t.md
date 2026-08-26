---
type: is
id: is-01m0x3h04eqf4a6q8d5z5t4g3t
title: Upgrade Repren to the current Flowmark process
kind: task
status: in_progress
priority: 1
version: 9
docs:
  - path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
    role: qa
    title: Flowmark process and migration review
refs:
  - kind: pr
    url: https://github.com/jlevy/repren/pull/53
    at: 2026-08-26T02:46:50.536Z
delegate: codex@spud10.local
labels:
  - tooling
  - docs
dependencies: []
hold: null
hold_until: null
created_at: 2026-08-25T18:39:36.588Z
updated_at: 2026-08-26T02:46:51.200Z
started_at: 2026-08-26T02:45:50.582Z
closed_at: null
close_reason: null
resolution: null
duplicate_of: null
---
Compare Repren Flowmark usage with the latest jlevy/flowmark release and project guidance; review the maintained Flowmark skill before installation; update pins, commands, CI, agent routing, and documentation as appropriate; install the skill at the correct scope; validate formatting and the full project; commit, push, and confirm CI.

## Notes

Repren PR #53 created with tbd shortcut create-or-update-pr-simple; waiting for the final GitHub Actions matrix before closing.
