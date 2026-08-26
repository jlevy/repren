---
type: is
id: is-01m0y2smt2847k14bvafc5kger
title: Publish and verify Repren 3.1.1
kind: task
status: closed
priority: 1
version: 3
labels: []
dependencies: []
created_at: 2026-08-26T03:46:05.762Z
updated_at: 2026-08-26T03:54:19.917Z
closed_at: 2026-08-26T03:54:19.916Z
close_reason: "Published Repren 3.1.1 from exact origin/master commit 885ce5e. Clean local release gates passed (113 pytest tests, 97 golden sessions, lint/type/Flowmark/generated-doc checks, build and artifact inspection). GitHub release and tag target the validated commit; publish workflow 32928053169 passed validate/build/publish. PyPI exposes the wheel and sdist with zero runtime dependencies, Python >=3.10,<4.0 and Typing :: Typed; registry SHA-256 digests match the workflow artifacts. No-cache exact-version smoke tests verified CLI version, updated docs, a live replacement, and byte-identical skill installation to both agent surfaces. Optional PyPI environment binding remains tracked in rpy-j2bz."
resolution: null
duplicate_of: null
---
Perform the complete patch-release process from the clean merged default branch: verify release delta and publisher configuration, run all local validation and clean artifact smoke tests, create GitHub release 3.1.1, watch the tag-driven publish workflow, verify PyPI metadata/artifacts, and smoke-test exact-version CLI docs and skill installation from PyPI. Do not declare completion until the released artifact and skill experience are verified end to end.
