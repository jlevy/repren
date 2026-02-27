---
type: is
id: is-01kjf2qz1wcns2pvh644a0cfzs
title: "P2: Expand replacement and overlap semantics tests"
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
created_at: 2026-02-27T08:16:48.699Z
updated_at: 2026-02-27T08:24:04.385Z
closed_at: 2026-02-27T08:24:04.383Z
close_reason: Expanded replacement/overlap semantics test coverage and validated pass.
---
Add unit tests for simultaneous replacement edge cases, overlap rules, capture-group behavior, and multiline options.

## Notes

Added targeted replacement/parsing tests: parse_patterns comments/blank/invalid handling, literal escaping, word-break wrapping, preserve-case variants, invalid regex raise, plus overlap-oriented multi_replace coverage. Coverage improved to 48% total (repren.py 51%).
