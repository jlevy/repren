---
type: is
id: is-01m0x3x868gh7ntryy4qf896p5
title: Fix the Flowmark Rust skill installer fallback pin
kind: bug
status: open
priority: 2
version: 2
docs:
  - path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
    role: research
    title: Flowmark installer mismatch evidence
labels:
  - upstream
  - flowmark
dependencies: []
created_at: 2026-08-25T18:46:18.050Z
updated_at: 2026-08-25T18:57:43.611Z
---
Flowmark Rust v0.3.2's --install-skill emits a Python fallback pinned to flowmark==0.7.2, while Flowmark v0.7.3 is current and its docs state that Python and Rust installers ship the same bundle. Reproduce in a clean directory, update flowmark-rs's embedded bundle/version metadata from jlevy/flowmark v0.7.3, add a cross-installer byte-equivalence/idempotency regression test, and submit the fix upstream. Repren should continue installing its project skill with the exact Python flowmark==0.7.3 release until a corrected Rust release is verified.
