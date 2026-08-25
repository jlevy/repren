---
type: is
id: is-01m0wsgya2bpcpr499t93aj6pq
title: Validate the tbd and simple-modern-uv upgrade end to end
kind: task
status: closed
priority: 2
version: 3
spec_path: docs/project/research/current/review-2026-08-25-simple-modern-uv-v0.5.0.md
labels:
  - validation
dependencies: []
parent_id: is-01m0wrdh4byt5cjcaj9v7440f2
created_at: 2026-08-25T15:44:48.961Z
updated_at: 2026-08-25T16:24:32.446Z
closed_at: 2026-08-25T16:24:32.445Z
close_reason: "Final clean validation passed: lint/type/docs, 113 pytest cases on Python 3.10-3.14, 97 Tryscript sessions, locked build, isolated wheel/sdist smoke, Python/npm audits, workflow/config syntax, artifact metadata, and tbd doctor."
resolution: null
duplicate_of: null
---
Run clean lint, generated-doc checks, unit tests, golden coverage, Tryscript sessions, the Python 3.10-3.14 matrix, builds, artifact smoke tests, dependency audits, tbd doctor, and final diff review before closing the parent upgrade.

## Notes

Clean validation started after resolving the direct Copier migration and staging the intended diff.
