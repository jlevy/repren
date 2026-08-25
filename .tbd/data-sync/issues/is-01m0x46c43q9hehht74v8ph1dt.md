---
type: is
id: is-01m0x46c43q9hehht74v8ph1dt
title: Harden Flowmark skill installation guidance for transitive dependencies
kind: task
status: open
priority: 2
version: 2
docs:
  - path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
    role: research
    title: Flowmark installer threat-model review
labels:
  - upstream
  - flowmark
  - supply-chain
dependencies: []
created_at: 2026-08-25T18:51:16.988Z
updated_at: 2026-08-25T18:57:43.836Z
---
Flowmark's project setup recommends an exact top-level Python installer command, but flowmark==0.7.3 resolves five compatible transitive packages. On 2026-08-25 a bare resolution selected marko 2.2.4, uploaded 2026-08-12 and still inside Repren's 14-day gate; the gated graph selected marko 2.2.3. Update jlevy/flowmark guidance/tests to make the installer threat model explicit and use a reviewed cool-off, lock/constraints, or the zero-dependency Rust installer once its stale bundle is fixed. Exact top-level pins prevent version drift of Flowmark itself but do not freeze or vet its dependency graph.
