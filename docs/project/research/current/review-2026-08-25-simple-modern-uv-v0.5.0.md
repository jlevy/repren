# Simple Modern uv v0.5.0 Migration Review

**Last Updated**: 2026-08-25

**Status**: Complete

**Related**:

- Repren upgrade bead: `rpy-1p85`
- Simple Modern uv follow-up bead: `rpy-z0un`
- [Simple Modern uv](https://github.com/jlevy/simple-modern-uv)
- [Copier update documentation](https://copier.readthedocs.io/en/stable/updating/)

* * *

## Purpose

Record template-level improvements found while updating Repren from Simple Modern uv
v0.2.20 to v0.5.0. This review separates genuine template issues from intentional Repren
customizations so that the follow-up pull request stays broadly useful.

The document covers the clean migration, validation, and smoke-test pass.
Each finding includes observed evidence, its user impact, and a concrete proposed
change.

## Executive Summary

Copier’s update model supports moving directly from the recorded template revision to a
newer revision: it reconstructs the old render, computes the project’s local delta, and
reapplies that delta to the new template.
Requiring every intervening release does not improve that model by default.
In Repren’s migration, the first incremental hop already produced six conflicts, while a
direct update produced one coherent conflict set against the desired final state.

The update policy should therefore make direct-to-latest the default, validate it in an
isolated worktree or clone, and reserve intermediate releases for diagnosis when the
direct result is ambiguous or a migration explicitly requires staging.
The template’s test strategy should cover upgrades from representative older tags so
maintainers can detect long-range migration problems before users encounter them.

## Findings

### SMUV-01: Make Direct-to-Latest the Default Update Path

**Status**: Confirmed

**Evidence**:

- The existing skill required one-release-at-a-time updates when a project was more than
  one release behind.
- Repren was ten tagged releases behind, from v0.2.20 to v0.5.0.
- The first incremental update, v0.2.20 to v0.2.21, produced six conflicted files before
  any later release could be applied.
- A direct v0.2.20 to v0.5.0 trial completed with one final conflict set.
  The conflicts corresponded to real Repren customizations such as its README, test
  harness, Python support range, and release-tag convention.
- Copier documents direct updates as its standard update mechanism.
  Version-gated migrations are selected by comparing the old and new template versions,
  so eligible migrations can still run across a multi-release jump.

**Impact**: Mandatory sequential updates multiply conflict resolution, validation work,
and temporary commits.
They also make users reconcile obsolete intermediate states that will immediately be
replaced.

**Proposed change**:

1. Recommend a direct update to the selected target tag.
2. Trial the update in an isolated clone or worktree and inspect the result before
   changing the working branch.
3. Use an intermediate release only when a migration declares a staging requirement or
   the direct update needs diagnosis.
4. Diagnose difficult ranges with targeted checkpoints or bisection instead of walking
   every tag.

### SMUV-02: Test Upgrades From Representative Historical Tags

**Status**: Confirmed

**Evidence**: The direct migration exercised a larger local delta than a freshly
generated project and exposed conflicts that a current-template generation test cannot
cover.

**Impact**: Without historical update fixtures, update guidance can become more
conservative than Copier requires because maintainers lack evidence about which older
states still migrate cleanly.

**Proposed change**:

1. Add CI fixtures for a recent tag, a pre-policy-change tag, and the oldest supported
   update baseline.
2. Give each fixture a small, realistic customization delta.
3. Run `copier update` directly to the candidate tag and assert that the generated
   project passes template validation.
4. Document unsupported source tags or genuinely staged migrations explicitly.

### SMUV-03: Document the Customizations an Update Must Preserve

**Status**: Confirmed

**Evidence**: Repren intentionally differs from the latest template in three important
ways: it still supports Python 3.10, keeps its package at the repository root, and uses
unprefixed release tags.
Those choices appeared in conflicts alongside ordinary template improvements.

**Impact**: Treating all conflicts as stale project code would silently break supported
Python versions, package discovery, or release automation.

**Proposed change**: Extend the update checklist with an explicit inventory of supported
Python versions, package layout, release-tag format, generated-document sources, extra
test suites, and publication settings.
Require each difference to be preserved, adopted, or retired intentionally.

### SMUV-04: Keep Supply-Chain Controls in Operational Configuration

**Status**: Confirmed

**Evidence**: Repren has no runtime dependencies, yet its README contained optional
cool-off and exact-pin advice in the primary installation path.
The v0.5.0 template adds project-owned `uv.toml` and workflow-level cool-off settings,
which are more reliable places for resolution policy.

**Impact**: Repeating operational policy in end-user installation prose distracts from a
simple install and can drift from the commands that CI and maintainers actually run.

**Proposed change**: Keep the generated project README concise.
Put maintainer policy in `uv.toml`, CI, the Makefile, and the dedicated supply-chain
document. Installation docs may explain exact application pins when that advice directly
affects the user.

### SMUV-05: Avoid a Stale Hard-Coded Python in the Installation Guide

**Status**: Confirmed

**Evidence**: The v0.5.0 project metadata and CI matrix include Python 3.14, but the
generated installation guide still says `uv python install 3.13`.

**Impact**: A newly generated project presents an older interpreter as the current
example immediately after generation.
The mismatch is small but undermines confidence that the template’s supported-version
surfaces move together.

**Proposed change**: Either render the example from one source of truth shared with the
CI matrix or use `uv python install` without a hard-coded version when the specific
version is not important.

### SMUV-06: Inventory and Lock Non-Python Developer Tools

**Status**: Confirmed

**Evidence**: Repren’s golden tests used `npx tryscript@latest`. Changing that to an
exact top-level version still left ranged transitive npm dependencies unresolved on each
run. The migration therefore added a small `package.json` and `package-lock.json`, with
`npm ci` installing the development-only runner reproducibly.

**Impact**: `uv.lock`, `uv.toml`, and `UV_EXCLUDE_NEWER` do not govern tools fetched by
another ecosystem. An update can appear fully pinned while CI still executes a changing
transitive dependency graph.

**Proposed change**: Add non-Python package managers and zero-install runners to the
customization inventory.
The update workflow should require an exact version and native lockfile for any such
tool, or record a deliberate exception when locking is impractical.

### SMUV-07: Render Project-Specific Publishing Instructions

**Status**: Confirmed

**Evidence**: The generated publishing guide links to the template repository’s workflow
and retains `OWNER`, `PROJECT`, `main`, and `vX.Y.Z` placeholders even though Copier
already knows the package name and GitHub owner.
Existing projects may also use a different default branch or tag convention.

**Impact**: Release instructions need manual correction after generation and can direct
maintainers to the wrong workflow, branch, compare URL, or tag format during an update.

**Proposed change**: Render all known repository and package values.
Either ask for the default branch and tag-prefix convention or prominently list those
fields in the post-generation customization checklist.

### SMUV-08: Treat Agent Instructions as a Protected Policy Surface

**Status**: Confirmed

**Evidence**: Repren’s `AGENTS.md` contains mandatory project-document routing,
supply-chain rules, and the tbd integration.
The v0.5.0 render contains useful generic defaults but also assumes a `src/` layout and
would replace repository-specific policy if accepted wholesale.

**Impact**: A careless conflict resolution can change how every later agent works and
can erase controls unrelated to Python packaging.

**Proposed change**: Call out `AGENTS.md` and equivalent instruction files as protected
merge surfaces. Updates should merge applicable new guidance into local instructions,
never treat the latest template render as authoritative for the whole file.

### SMUV-09: Make `UV_CONFIG_FILE` Absolute in CI

**Status**: Confirmed

**Evidence**: The v0.5.0 workflows export `UV_CONFIG_FILE=uv.toml`. Repren tests that
change to a temporary directory and launch a child `uv run` inherit that relative value.
The child process then fails with `failed to open file uv.toml` because the path is
resolved from its new working directory.
The generated Makefile avoids the problem by exporting `$(CURDIR)/uv.toml`.

**Impact**: A test or build step can fail solely because it changes directories, even
though the project configuration exists and the lock is valid.
The same issue can affect scripts that invoke uv from a subdirectory.

**Proposed change**: Set the workflow value to `${{ github.workspace }}/uv.toml`,
matching the Makefile’s absolute-path behavior.
Add a template validation that changes directory before launching a child uv command.

### SMUV-10: Audit Tool Pins at Project-Update Time

**Status**: Confirmed

**Evidence**: v0.5.0 renders uv 0.12.0 in both workflows.
By the Repren migration date, uv 0.12.3 had cleared the 14-day cool-off and was the
newest eligible patch.
uv 0.12.4 and 0.12.5 and setup-uv v10 were still inside the gate.
The workflow therefore needed a separate version and checksum review after applying the
latest template tag.

**Impact**: “Latest template” and “latest eligible tool pins” are different properties.
A project can complete a correct Copier update and still retain an older eligible patch
of a pinned bootstrap tool.

**Proposed change**: Make the update workflow explicitly query primary releases for
GitHub Actions, uv, and other exact-pinned runners.
Upgrade only versions that clear the cool-off, update associated checksums atomically,
and record why newer releases remain held.

### SMUV-11: Define the Source-Distribution Inclusion Policy

**Status**: Confirmed

**Evidence**: The Repren wheel is 35 KiB and contains only package/runtime material.
The default Hatch sdist is 754 KiB and includes the full tracked repository, including
agent integration files, tbd documentation, npm development locks, research, and
workflow configuration.
The published 3.1.0 sdist was 306 KiB before the expanded repository tooling.

**Impact**: The build is valid, but new template integrations can silently increase the
published source artifact and expose repository-management material that is not needed
to build or understand the package.

**Proposed change**: Choose and document an sdist policy.
Either provide an explicit allowlist for build inputs, source, tests, license, and
user-facing docs, or exclude known internal integration directories.
Add an artifact-content assertion to template validation so growth is intentional.

### SMUV-12: Preserve Existing Lint and Type-Check Strictness

**Status**: Confirmed

**Evidence**: The v0.5.0 render adds a global Ruff `E402` exemption and disables two
BasedPyright checks for incomplete or unnecessary ignore comments.
Repren passed those checks before the update and continued to pass after the new
suppressions were removed.

**Impact**: Treating a new-project default as authoritative during an update can
silently weaken an established project’s quality gates without resolving any actual
finding.

**Proposed change**: Include lint selections, ignore lists, and type-checker
suppressions in the customization inventory.
Merge new settings individually and require a concrete failing case before broadening an
existing project’s exemptions.

### SMUV-13: Isolate Trusted-Publishing Permission

**Status**: Confirmed

**Evidence**: The v0.5.0 publish workflow grants `id-token: write` to the job that
checks out the repository, installs all development dependencies, runs tests, and builds
the package. Any compromised code executed in that job can request the same OIDC token
used for PyPI trusted publishing.

**Impact**: Exact locks and disabled caches reduce risk but do not provide least
privilege. The sensitive publishing credential is available across a much larger
execution surface than necessary.

**Proposed change**: Use three jobs: unprivileged full validation; a fresh build that
installs only the exact-pinned build group; and a minimal publisher.
Transfer only `dist/*` through full-SHA-pinned official upload and download actions.
Grant `id-token: write` only to the last job, which should not check out or execute
project code.

### SMUV-14: Apply Cool-Off Exceptions Only to the Approved Package

**Status**: Confirmed

**Evidence**: Tryscript 0.2.1 had a maintainer-approved first-party exception to the
14-day cool-off, but a normal npm lock resolution also selected third-party `ansi-regex`
6.3.0, published 13 days before the review date.
The ambient npm `before` setting enforced a different window, while npm warned that the
ambient `minimum-release-age` setting was unsupported.

**Impact**: Temporarily lifting an ecosystem-wide release-age gate for one approved
package can silently admit unrelated recent transitive releases.
A lockfile makes that selection reproducible but does not make it compliant with the
intended exception.

**Proposed change**: Require an ecosystem-wide publication-date audit after any cool-off
exception. Constrain recent third-party transitive packages to the newest eligible
release with the package manager’s native override mechanism, and record the constraint
beside the exception.
Update the supply-chain guidance with a tested npm procedure rather than relying on
unsupported configuration keys.

## Follow-Up Pull Request Scope

The follow-up Simple Modern uv pull request should initially include:

1. The direct-to-latest policy correction in the skill’s update instructions.
2. Historical migration tests or a focused test-plan issue if the fixture work is too
   large for the policy pull request.
3. A customization inventory in the update workflow.
4. Fixes for stale Python examples and project-specific publishing docs.
5. Guidance for locked tools outside the Python dependency graph.
6. Absolute `UV_CONFIG_FILE` handling in generated workflows.
7. Update-time audits for eligible action and tool pins.
8. An explicit source-distribution inclusion policy or a focused follow-up issue.
9. Selective preservation of existing lint and type-check strictness.
10. Least-privilege separation for the trusted-publishing job.
11. Package-scoped cool-off exceptions and a tested npm publication-date audit.
12. Any additional findings confirmed by Repren’s final validation.

## Open Questions

1. Which historical template tags should receive explicit update guarantees?
2. Should the migration test matrix live in the template repository’s CI or in a
   reusable validation script invoked locally and in CI?
3. Does the generated installation guide need user-facing supply-chain prose after
   `uv.toml` and pinned CI actions are in place?

## Repren Final Review

**Verdict**: Clean; no blocking findings remain.

### Resolved Findings

- **RPR-01 (High), `tests/pytests.py`**: The pytest integration bridge still invoked
  `tryscript@latest`, bypassing the new npm lock.
  It now uses `npx --no-install tryscript`; a test with an unreachable npm registry
  confirmed that no fetch occurs.
- **RPR-02 (High), `.github/workflows/publish.yml`**: Project development code and
  dependencies ran with `id-token: write`. The workflow now validates without publish
  permission, builds from a fresh checkout with only the locked build group, and gives
  OIDC permission only to a job that downloads and publishes the distributions.
- **RPR-03 (Medium), `.github/workflows/*.yml`**: Relative `UV_CONFIG_FILE` values broke
  child uv commands after a working-directory change.
  Both workflows now use the absolute GitHub workspace path.
- **RPR-04 (Medium), `pyproject.toml`**: The template render would have weakened Ruff
  and BasedPyright checks that Repren already passed.
  The unnecessary suppressions were removed and the strict configuration passes.
- **RPR-05 (Low), `repren/skills/SKILL.md`**: Flowmark emitted trailing whitespace on a
  quoted blank line. Separating the quote blocks preserved the rendering and satisfies
  `git diff --check`.
- **RPR-06 (High), `package-lock.json`**: The first-party Tryscript exception had also
  admitted third-party `ansi-regex` 6.3.0 before it cleared the 14-day gate.
  `package.json` now overrides it to the newest eligible release, 6.2.2, while keeping
  Tryscript itself at the explicitly approved 0.2.1.
- **RPR-07 (Low), `docs/development.md`**: The golden-test command said the Tryscript
  version was pinned in the Makefile, but the Makefile only invokes the installed
  binary. The guide now identifies `package.json` and `package-lock.json` as the actual
  version and graph pins.

### Design Assessment

The final design treats the template as a source of reviewed changes, not an authority
over established project decisions.
Repren retains Python 3.10, its root package layout, unprefixed release tags,
generated-doc source, golden suites, and repository agent policy.
Project-owned uv configuration and both ecosystem lockfiles make local, CI, and release
resolution reproducible.

The release pipeline follows least privilege across validation, build, and publishing.
The remaining broad sdist contents are valid and contain no runtime dependencies, but
SMUV-11 tracks the opportunity to define a narrower upstream policy.

### Documentation

Developer, installation, publishing, supply-chain, active Tryscript migration, README,
embedded module, and skill documentation now match the implemented commands.
Generated outputs were regenerated from `docs/repren-docs.md` and verified stable.

### Validation Results

- A clean lockfile install, lint, BasedPyright, Flowmark, generated-document check, unit
  suite, golden coverage, Tryscript suite, and build all passed from the final source
  state.
- All 113 pytest cases passed independently on Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- All 97 Tryscript sessions passed through the exact `tryscript` 0.2.1 npm lock.
  The pytest bridge also passed with the npm registry set to an unreachable address,
  confirming that `npx --no-install` performs no network fetch.
- The wheel and source distribution installed and ran in separate isolated Python 3.10
  environments. The wheel metadata requires Python 3.10 through 3.x and declares no
  runtime dependencies.
- `pip-audit` 2.10.1 and `npm audit` reported no known vulnerabilities.
  The Python audit skipped only the editable Repren project itself.
- Registry publication metadata confirms that every locked npm package except the
  explicitly approved first-party Tryscript release cleared the 14-day gate.
- The uv lock check, npm lock install, Copier and workflow YAML parsing, JSON parsing,
  shell syntax checks, conflict-marker scan, whitespace checks, and `tbd doctor` all
  passed.
- The three-job publishing design was exercised locally through its isolated,
  build-group-only build step; both distributions were produced successfully.

## References

- [Copier: Updating a Project](https://copier.readthedocs.io/en/stable/updating/)
- [Copier: Configuring a Template](https://copier.readthedocs.io/en/latest/configuring/)
- [Simple Modern uv repository](https://github.com/jlevy/simple-modern-uv)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
