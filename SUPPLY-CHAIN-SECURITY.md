# Supply-Chain Security

This repository adopts the 14-day cool-off, disabled-install-script, and lockfile
practices from
[Supply Chain Hardening](https://github.com/jlevy/supply-chain-hardening).
Before adding or upgrading a dependency, also load
`tbd guidelines supply-chain-hardening`. This is the balanced baseline.
Use stricter source review or isolation for an untrusted repository or a runner with
broader production or publishing authority.

Repren’s published package has zero runtime dependencies.
The development and release toolchain is separate: those tools execute with contributor
or CI privileges and receive the full policy unless an explicit exception below says
otherwise.

## Repren’s Zero-Dependency Runtime

`dependencies = []` in `pyproject.toml`, and the installed package imports only the
Python standard library.
`uv tool install repren` and `uvx repren@latest` therefore fetch Repren itself without a
transitive runtime tree.

The README uses `@latest` deliberately so people and agents get the current
self-documenting CLI and skill installer.
This is an exception to the usual exact-pin rule for zero-install runners, scoped only
to Repren’s own zero-dependency package.
The choice favors current user-facing behavior over reproducibility.
Zero dependencies remove transitive-package risk, but do not protect against a
compromised Repren release or publishing account.
Privileged or reproducible environments may impose an exact Repren version in their own
deployment policy; the primary README stays concise.
This exception does not relax development-tool controls.

## Development Dependencies

Python development and build dependencies are declared in `pyproject.toml` and locked in
`uv.lock`. Project-owned settings in `uv.toml` require uv 0.12 and exclude releases
newer than 14 days during resolution.
The Makefile and GitHub workflows select that configuration explicitly so ambient user
or runner settings cannot change the lock.

Use the checked-in workflows:

```bash
make install       # Install uv-locked groups and npm-locked golden-test tooling.
make upgrade       # Resolve compatible Python upgrades through the 14-day gate.
make lint-check
make test
make build
```

When changing dependencies:

1. Confirm the dependency is necessary, correctly named, actively maintained, and
   obtained from its official registry or repository.
2. Use the ecosystem’s native lockfile and review the complete lockfile diff.
3. Keep install scripts disabled where the toolchain permits it.
4. Run vulnerability audits and the full test suite.
   Audits report known advisories; they do not establish that a package is benign.
5. Document any cool-off exception, exact version, reason, and human approval.

For a reviewed fresh Python release, keep the global gate and add an absolute
`exclude-newer-package` cutoff to `uv.toml` just after the approved release’s final
artifact upload. Resolve only that package with
`UV_CONFIG_FILE="$PWD/uv.toml" uv lock --upgrade-package package-name`, inspect the
complete lock diff, and commit the configuration with `uv.lock` so locked CI sees the
same policy. Remove the exception and relock after the release clears the normal window.

CI uses `uv sync --locked --all-extras --all-groups`, which installs from the committed
lock and fails when `pyproject.toml` would require it to change.
The release workflow validates with the full development toolchain, then builds from a
fresh checkout with only the exact-pinned build group.
A third job receives only the distributions and is the only one with `id-token: write`;
it does not check out or execute project or development code.
The workflow runs only for a published GitHub Release and declares the `pypi`
environment. PyPI enforces that environment only when Repren’s Trusted Publisher is
constrained to the same name; a blank existing setting remains compatible but
unconstrained. This separation limits credential exposure.
The release-only trigger removes the ordinary manual-branch path, but it does not
override repository permissions: anyone allowed to create a matching release tag may
still invoke it. If repository writers who should not publish are added, restrict
creation and updates of version tags to release maintainers with a tag ruleset and/or
require an environment reviewer.
It does not make the source or distributions safe: the build job executes repository and
build-backend code, and the final job publishes its output.

## Non-Python Development Tools

Flowmark is an exact-pinned zero-install tool:

- `flowmark-rs==0.3.2` runs through `uvx` and the project cool-off.

Tryscript is installed through npm:

- `tryscript==0.2.1` is exact-pinned in `package.json`.
- `package-lock.json` fixes its transitive graph.
- `npm ci --ignore-scripts` installs that graph locally and in CI.
- Version 0.2.1 was published inside the normal cool-off window.
  The user explicitly approved it as a first-party exception because they maintain
  Tryscript. The exception applies only to the release-age gate; the exact pin, lockfile
  review, disabled scripts, audit, and tests still apply.
- The exception does not cover third-party transitive packages.
  `ansi-regex` is overridden to exact version 6.2.2 because 6.3.0 had not cleared the
  14-day gate when this lockfile was created.

## Quick Reference

| Context | Rule |
| --- | --- |
| Running Repren | Zero runtime dependencies; the documented `uvx repren@latest` is deliberate. |
| Python development tools | Resolve through `uv.toml`, commit `uv.lock`, and install with `--locked` in CI. |
| Flowmark | Exact-pinned at 0.3.2 and subject to the uv cool-off. |
| Tryscript | Exact-pinned and npm-locked at 0.2.1; first-party release-age exception approved on 2026-08-25, with third-party transitive packages still gated. |
| Publishing | Build from a clean, tested release tag; publish only through the `pypi` environment, with OIDC isolated from project code. |

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
