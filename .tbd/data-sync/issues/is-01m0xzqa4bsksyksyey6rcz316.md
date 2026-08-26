---
type: is
id: is-01m0xzqa4bsksyksyey6rcz316
title: Assess merged Repren changes for release readiness
kind: task
status: closed
priority: 1
version: 6
delegate: codex@spud10.local
labels:
  - release
  - review
dependencies: []
hold: null
hold_until: null
created_at: 2026-08-26T02:52:23.560Z
updated_at: 2026-08-26T03:43:08.566Z
started_at: 2026-08-26T02:52:28.045Z
closed_at: 2026-08-26T03:43:08.565Z
close_reason: Release assessment corrected to treat versioned documentation as part of the installed agent-skill experience. Recommend 3.1.1 after the PyPI publisher environment check; no runtime or installer API change warrants 3.2.0.
resolution: null
duplicate_of: null
---
Check out the merged remote default branch, compare it with the latest GitHub and PyPI release, identify user-visible and shipped-content changes, inspect any additional unreleased commits, and recommend whether to release now and at what semantic-version level. Do not create a tag or release without separate authorization.

## Notes

Correction: Flowmark --install-skill materializes a two-file documentation bundle (.agents/skills/flowmark/SKILL.md plus references/project-setup.md), both newly present since Repren 3.1.0, alongside new AGENTS.md and development guidance. Those repository-agent files are not Repren wheel content and are excluded from the narrowed sdist, although docs/development.md is included in the sdist. Separately, Repren agent_skill.py is unchanged and its copied SKILL.md has only Flowmark reflow, but that skill explicitly delegates usage to repren --docs/--help. Those versioned CLI docs changed materially, so a 3.1.1 release is required for uvx repren@latest and skill-driven users to receive the corrected guidance. This strengthens the case for a patch release, without changing the semver recommendation.
