# Supply-Chain Security

This repository adopts the 14-day cool-off, disabled-install-script, and lockfile
practices from
[Supply Chain Hardening](https://github.com/jlevy/supply-chain-hardening).
Before adding or upgrading a dependency, also load
`tbd guidelines supply-chain-hardening`.

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
It does not relax development-tool controls.

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
5. Document any cool-off exception, exact version, reason, and human approval.

CI uses `uv sync --locked --all-extras --all-groups`, which installs from the committed
lock and fails when `pyproject.toml` would require it to change.
The release workflow validates with the full development toolchain, then builds from a
fresh checkout with only the exact-pinned build group.
A third job receives only the distributions and is the only one with `id-token: write`;
it cannot execute project or development code.

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
| Publishing | Build from a clean, tested tag with GitHub trusted publishing. |

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
