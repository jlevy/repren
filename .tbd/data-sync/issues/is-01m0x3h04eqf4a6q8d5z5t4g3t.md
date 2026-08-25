---
type: is
id: is-01m0x3h04eqf4a6q8d5z5t4g3t
title: Upgrade Repren to the current Flowmark process
kind: task
status: closed
priority: 1
version: 5
docs:
  - path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
    role: qa
    title: Flowmark process and migration review
labels:
  - tooling
  - docs
dependencies: []
created_at: 2026-08-25T18:39:36.588Z
updated_at: 2026-08-25T18:59:25.809Z
closed_at: 2026-08-25T18:59:25.808Z
close_reason: Current Flowmark process installed, reviewed, validated, committed in 87034df and afd26e3, and pushed. Upstream installer follow-ups remain independently tracked as rpy-r7iu and rpy-ncar.
resolution: null
duplicate_of: null
---
Compare Repren Flowmark usage with the latest jlevy/flowmark release and project guidance; review the maintained Flowmark skill before installation; update pins, commands, CI, agent routing, and documentation as appropriate; install the skill at the correct scope; validate formatting and the full project; commit, push, and confirm CI.

## Notes

Verified latest releases: flowmark 0.7.3 and flowmark-rs 0.3.2. Installed the reviewed 0.7.3 skill globally and project-locally; exact tagged skill bytes and installer idempotency verified. Adopted recursive discovery with explicit generated/vendor/golden exclusions, exact Rust runner, safe auto-staging hook with partial-staging and generated-mirror guards, local check target, and no ordinary Markdown CI gate. Full Repren suite, builds, audits, formatter parity, and isolated hook smoke tests pass. Rust installer mismatch and Python-installer transitive risk are split into rpy-r7iu and rpy-ncar.
