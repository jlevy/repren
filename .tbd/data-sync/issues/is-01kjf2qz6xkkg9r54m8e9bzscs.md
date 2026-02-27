---
type: is
id: is-01kjf2qz6xkkg9r54m8e9bzscs
title: "P3: Expand filesystem mutation and collision tests"
kind: task
status: closed
priority: 1
version: 5
spec_path: docs/project/specs/active/plan-2026-02-27-rust-port-prep-and-test-hardening.md
labels: []
dependencies:
  - type: blocks
    target: is-01kjf2qzmtz7g58ycj6gjp89r0
parent_id: is-01kjf2qyp00yq4mv4fyr93pacv
created_at: 2026-02-27T08:16:48.859Z
updated_at: 2026-02-27T08:24:04.376Z
closed_at: 2026-02-27T08:24:04.375Z
close_reason: Expanded filesystem mutation/collision tests and validated pass.
---
Add tests for rename collisions, directory moves, backup suffix behavior, and undo/clean lifecycle edge cases.

## Notes

Added filesystem edge-case tests for temp-suffix skipping, explicit backup-file discovery, and move_file collision suffix fan-out.
