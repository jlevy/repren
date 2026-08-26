---
type: is
id: is-01m0x28ggfs726dpnyeg67hzf3
title: Constrain Repren PyPI Trusted Publisher to pypi environment
kind: chore
status: open
priority: 2
version: 3
labels: []
dependencies: []
created_at: 2026-08-25T18:17:29.870Z
updated_at: 2026-08-26T03:54:19.587Z
---
Before claiming environment-bound trusted publishing, verify Repren existing PyPI publisher and set its environment to pypi. A blank environment remains functionally compatible with the updated release-only workflow but is unconstrained. Do not require a GitHub reviewer while Repren has one maintainer. If repository writers who should not publish are added, restrict creation and updates of version tags to release maintainers with a tag ruleset and/or require an environment reviewer; a selected-tag environment filter alone does not restrict who creates a matching tag. Related: Simple Modern uv PR #31 and the 2026-08-25 migration review.

## Notes

On 2026-08-25/26, created the GitHub pypi environment with no reviewer or deployment-branch gate, matching the solo-maintainer policy. The Repren 3.1.1 release then published successfully through a job declaring environment: pypi, proving the existing PyPI Trusted Publisher with blank environment remains functionally compatible. The PyPI-side publisher setting could not be inspected or changed because the available browser session was not authenticated; keep this bead open until the project publisher is explicitly bound to pypi.
