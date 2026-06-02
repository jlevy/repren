# Supply-Chain Security

This repo **adopts** the **Supply-Chain Hardening** policy (the 14-day cool-off, disabled
install scripts, lockfile discipline). This file is the portable flag that tells any
agent or contributor the rules *before* they add or upgrade a dependency. The full
cross-ecosystem policy lives in `tbd guidelines supply-chain-hardening`; the complete
playbooks are at <https://github.com/jlevy/supply-chain-hardening>.

The runtime story is already clean (zero dependencies, below); the dev/CI toolchain is
mostly there, with a few unpinned zero-install runners tracked as known exceptions under
[Known exceptions](#known-exceptions).

## What's special about repren: zero runtime dependencies

repren has **zero runtime dependencies** (`dependencies = []` in `pyproject.toml`). It is
a single-file tool that imports only the Python standard library. So:

- **For people who *run* repren, supply-chain risk is minimal.** `uvx repren@latest` (or
  `uv tool install repren`) fetches and executes only repren itself — there is no
  transitive dependency tree to be compromised. This is exactly why the docs and the
  installed agent skill use `uvx repren@latest` rather than a pinned version: with no
  dependency tree, the usual reason to pin a zero-install runner mostly falls away.
- **A cool-off is still recommended, just lower-stakes.** If you want an extra safety
  margin against a compromised repren *release* itself, opt into uv's release cool-off so
  very recent uploads are skipped:

  ```bash
  # Skip uploads newer than 14 days, then run the latest within that window:
  UV_EXCLUDE_NEWER="14 days" uvx repren@latest --help
  ```

  Set `UV_EXCLUDE_NEWER` in your environment and it applies to every `uvx`/`uv` call,
  including the agent skill's invocations.

> **Deliberate exception to the "no unpinned runners" rule.** The hardening policy says to
> pin zero-install runners (`uvx pkg@version`, not `@latest`). repren takes the documented
> exception: because it has no dependency tree, `@latest` + the cool-off above gives the
> protection that pinning is meant to provide, with less version-management complexity.
> This exception is scoped to repren's *own* runner — it does **not** relax the cool-off
> for the development dependencies below.

## Development dependencies: the cool-off applies here

The zero-deps story is about *runtime*. The **dev toolchain** (in `[dependency-groups]`:
pytest, ruff, basedpyright, jinja2, rich, etc.) runs with full privileges during local
development, tests, and CI — historically the *more* dangerous surface, since build and
test tooling execute arbitrary code. The 14-day cool-off and the other install rules
apply in full here:

- **Cool-off (resolution-time gate).** Resolve dev dependencies with a release-age gate:

  ```bash
  export UV_EXCLUDE_NEWER="14 days"   # never resolve a version less than 14 days old
  uv sync --frozen                    # install the dev group from the committed lockfile
  ```

  Keep `UV_EXCLUDE_NEWER` in your shell profile (and in CI) so it covers every resolve.
- **Lockfile discipline.** `uv.lock` is committed. Install frozen (`uv sync --frozen` /
  `uv run --frozen`); never re-resolve in CI. Review a lockfile diff like a code diff.
- **Don't update for its own sake.** The safest upgrade is the one you skip. Bump a dev
  dependency only for a concrete reason, let it clear the cool-off, and review the diff.
- **Audit.** Run `uvx pip-audit` (or `uv run pip-audit`) and address findings before
  continuing. Prefer wheels over building sdists from source (`UV_NO_BUILD` /
  `--only-binary`) where feasible.
- **Exceptions are explicit and human-approved.** If a dev dependency version inside the
  14-day window is genuinely needed (e.g. a CVE patch), pin the exact version, record the
  reason and a `Reviewed-by:` sign-off in the PR, and confirm afterward it wasn't yanked.
  Agents never self-approve an exception.

## Known exceptions

Being honest about where the repo does not yet meet the policy, so agents don't read a
standard the workflow silently breaks:

- **`repren`'s own runner uses `@latest`, unpinned** (docs, README, and the installed
  `SKILL.md`). This is deliberate: repren has zero runtime dependencies, so `@latest`
  fetches only repren itself, and the recommended `UV_EXCLUDE_NEWER` cool-off covers the
  compromised-release case. See "What's special about repren," above.
- **Unpinned zero-install dev/CI runners.** A few development and CI commands still invoke
  zero-install runners without a version pin — `uvx flowmark@latest` (formatting, in the
  `Makefile`) and `npx tryscript@latest` (the golden test harness, in `.github/workflows/`
  and the dev docs). These run only at development/CI time, never for users of repren, but
  they do bypass the cool-off. They are tracked here to be pinned (or run under a CI-level
  `UV_EXCLUDE_NEWER`/`npm` release-age gate) in a follow-up; until then they are recorded
  exceptions, not an oversight.

## Quick reference

| Context | Rule |
| --- | --- |
| Running repren | Zero deps; `uvx repren@latest` is fine. Optional: `UV_EXCLUDE_NEWER="14 days"`. |
| Adding/upgrading a **dev** dependency | 14-day cool-off, lockfile-pinned, audited, reason on the record. |
| Dev/CI zero-install runners (flowmark, tryscript) | Tracked exception — to be pinned; see [Known exceptions](#known-exceptions). |
| Publishing repren | Build from a clean tag; prefer trusted publishing / provenance (see the guidebook). |

<!-- This document follows the Supply-Chain Hardening guideline
(tbd guidelines supply-chain-hardening) and common-doc-guidelines.md.
See github.com/jlevy/supply-chain-hardening before editing. -->
