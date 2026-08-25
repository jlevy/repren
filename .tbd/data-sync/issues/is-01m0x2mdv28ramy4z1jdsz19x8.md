---
type: is
id: is-01m0x2mdv28ramy4z1jdsz19x8
title: Narrow Repren source-distribution contents
kind: task
status: closed
priority: 2
version: 3
labels:
  - supply-chain
  - packaging
dependencies: []
created_at: 2026-08-25T18:24:00.350Z
updated_at: 2026-08-25T18:34:23.733Z
closed_at: 2026-08-25T18:34:23.731Z
close_reason: Added and documented the explicit Hatch sdist allowlist. The 83 KiB archive excludes workflows, agent integrations, tbd state, and internal project records; a wheel built from it installed and ran under isolated Python 3.10. Full Repren tests and artifact checks pass.
resolution: null
duplicate_of: null
---
Adopt an explicit Hatch sdist allowlist that preserves source, downstream tests, their small test harness, licensing, security guidance, and user-facing docs while excluding workflows, agent integrations, tbd state, and internal project records. Verify artifact contents and build/install from the sdist.
