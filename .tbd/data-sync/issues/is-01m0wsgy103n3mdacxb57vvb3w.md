---
type: is
id: is-01m0wsgy103n3mdacxb57vvb3w
title: Upgrade and lock tryscript 0.2.1
kind: task
status: closed
priority: 2
version: 5
spec_path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
labels:
  - testing
  - supply-chain
dependencies: []
parent_id: is-01m0wrdh4byt5cjcaj9v7440f2
created_at: 2026-08-25T15:44:48.671Z
updated_at: 2026-08-25T16:24:32.161Z
closed_at: 2026-08-25T16:24:32.159Z
close_reason: Tryscript 0.2.1 is exact-pinned in package.json/package-lock.json under the user's first-party cool-off exception; npm ci, all 97 sessions, the pytest bridge, npm audit, and an unreachable-registry no-fetch check passed.
resolution: null
duplicate_of: null
---
Upgrade Repren's first-party golden-test runner to tryscript 0.2.1, exact-pin it, lock transitive npm dependencies, run the golden suite, and record the user-approved first-party cool-off exemption.

## Notes

User-approved exception: tryscript is first-party and maintained by the user, so use latest 0.2.1 despite its 2026-08-22 release date. Keep the direct dependency exact and commit package-lock.json for its transitive graph.

Reopened: Final review found the pytest integration bridge still used tryscript@latest outside package-lock.json; reopen to fix and revalidate the locked path.
