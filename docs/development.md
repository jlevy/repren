# Development

## Setting Up uv

This project is set up to use [uv](https://docs.astral.sh/uv/) to manage Python and
dependencies. First, be sure you
[have uv installed](https://docs.astral.sh/uv/getting-started/installation/).

[Fork the project][project-fork] (having your own fork will make it easier to
contribute) and
[clone it](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

[project-fork]: https://github.com/jlevy/repren/fork

The golden-test runner also requires Node.js 20 or newer and npm.
Node is development tooling only; it is not part of Repren’s Python package or runtime.

## Basic Developer Workflows

The `Makefile` simply offers shortcuts to `uv` commands for developer convenience.
(For clarity, GitHub Actions don’t use the Makefile and just call `uv` directly.)

```shell
# Select only the checked-in uv settings so ambient user configuration cannot alter
# dependency resolution or make uv.lock nonportable. The Makefile does this itself.
export UV_CONFIG_FILE="$PWD/uv.toml"

# First, install all dependencies and set up your development environment.
# This installs the uv-locked Python groups and the npm-locked golden-test runner.
make install

# Install, lint, regenerate docs, and run the complete test suite:
make

# Build the wheel and source distribution:
make build

# Linting (auto-fixes formatting and lint issues):
make lint

# Linting in check-only mode, matching CI (fails on issues, does not modify files):
make lint-check

# Format the Markdown sources owned by Flowmark:
make format

# Check Markdown formatting without changing files:
make format-check

# Regenerate README.md and the embedded documentation in repren/repren.py:
make gendocs

# Regenerate docs and fail if the checked-in output was stale:
make gendocs-check

# Run unit tests, golden coverage gates, and golden integration tests:
make test

# Update golden baselines when output changes intentionally:
make update-golden

# Delete all the build artifacts:
make clean

# Upgrade dependencies to compatible versions:
make upgrade

# To run tests by hand:
uv run pytest   # all tests
uv run pytest -s tests/pytests.py  # one test file, showing output

# Run the CLI golden tests directly. The exact runner and its dependency graph are
# pinned in package.json and package-lock.json:
make test-golden

# Check the golden-test coverage and quality gates:
make test-golden-coverage

# Build and install current dev executables, to let you use your dev copies
# as local tools:
uv tool install --editable .

# Dependency management directly with uv:
# Add a new dependency:
uv add package_name
# Add a development dependency:
uv add --dev package_name
# Update to latest compatible versions (including dependencies on git repos):
uv sync --upgrade
# Update a specific package:
uv lock --upgrade-package package_name

# Run a shell within the Python environment:
uv venv
source .venv/bin/activate
```

See [uv docs](https://docs.astral.sh/uv/) for details.

## Test Infrastructure

Repren uses two complementary test layers:

- `tests/pytests.py` contains pytest unit and integration coverage for parsing, case
  conversion, rewriting, renaming, backup management, JSON output, and CLI errors.
- `tests/tryscript/*.tryscript.md` contains fixture-first golden sessions that exercise
  the installed CLI end to end.
  `package-lock.json` fixes the runner and its transitive dependencies.
  The shell coverage gate checks that important behavior families remain represented and
  rejects fragile test patterns.

When output changes intentionally, run `make update-golden`, review every changed
session, then run `make test` again.
Generated documentation has a separate source of truth in `docs/repren-docs.md`; update
that source and run `make gendocs` rather than editing `README.md` or the embedded
module documentation by hand.

## IDE Setup

If you use VSCode or a fork like Cursor or Windsurf, you can install the following
extensions:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

- [Based Pyright](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright)
  for type checking. Note that this extension works with non-Microsoft VSCode forks like
  Cursor.

## Supply Chain Hardening

Dependencies are an attack surface.
Before adding or upgrading any dependency, follow
[**supply-chain-hardening**](https://github.com/jlevy/supply-chain-hardening), a concise
cross-ecosystem guide on installing dependencies safely.
Its key defaults:

- **Cool-off period:** Don’t install or upgrade to a release less than 14 days old
  (absent a documented exception); most malicious publishes are caught within days.
  uv supports a relative
  [dependency cooldown](https://docs.astral.sh/uv/concepts/resolution/#dependency-cooldowns)
  such as `"14 days"`. This project records the policy in `uv.toml`; the Makefile, CI,
  and examples select that file explicitly so user- or system-level
  [uv configuration](https://docs.astral.sh/uv/configuration/files/) cannot leak into
  the committed lockfile.
  Override it explicitly for a stricter window, such as
  `UV_EXCLUDE_NEWER="30 days" make upgrade`. A reviewed emergency exception must be
  equally explicit, using `UV_EXCLUDE_NEWER="0 days"` only for that invocation and
  recording why the normal gate was bypassed.

- **Vet before adding:** Confirm the package is actually needed and its name is spelled
  correctly (typosquats are common), and prefer a little first-party code over a new
  dependency.

- **Pin, lock, and audit:** Commit your `uv.lock`, pin GitHub Actions to a commit SHA or
  immutable tag, and run a vulnerability audit (e.g. `pip-audit`) after changes.

## Publishing Releases

See [publishing.md](publishing.md) for instructions on publishing to PyPI.

## Documentation

- [uv docs](https://docs.astral.sh/uv/)

- [basedpyright docs](https://docs.basedpyright.com/latest/)

* * *

*This file was built with
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
