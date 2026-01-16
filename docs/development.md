# Development

## Setting Up uv

This project is set up to use [uv](https://docs.astral.sh/uv/) to manage Python and
dependencies. First, be sure you
[have uv installed](https://docs.astral.sh/uv/getting-started/installation/).

Then [fork the jlevy/repren repo](https://github.com/jlevy/repren/fork) (having your own
fork will make it easier to contribute) and
[clone it](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Basic Developer Workflows

The `Makefile` simply offers shortcuts to `uv` commands for developer convenience.
(For clarity, GitHub Actions don’t use the Makefile and just call `uv` directly.)

```shell
# First, install all dependencies and set up your virtual environment.
# This simply runs `uv sync --all-extras` to install all packages,
# including dev dependencies and optional dependencies.
make install

# Run uv sync, lint, and test:
make

# Build wheel:
make build

# Linting:
make lint

# Run tests:
make test

# Update golden test baseline (when expected test output changes intentionally):
make update-golden

# Delete all the build artifacts:
make clean

# Upgrade dependencies to compatible versions:
make upgrade

# To run tests by hand:
uv run pytest   # all tests
uv run pytest -s tests/pytests.py  # one test, showing outputs

# Run integration tests:
./tests/run.sh

# Update golden test baseline (when expected test output changes intentionally):
make update-golden

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
# Update dependencies on a package:
uv add package_name@latest

# Run a shell within the Python environment:
uv venv
source .venv/bin/activate
```

See [uv docs](https://docs.astral.sh/uv/) for details.

## Test Infrastructure

The project uses two complementary test approaches:

### Unit Tests (`tests/pytests.py`)

Standard pytest unit tests for internal functions like case conversion, pattern parsing,
and backup management.

```shell
uv run pytest tests/pytests.py
```

### Golden Tests (`tests/golden-tests.sh`)

Shell-based integration tests that exercise the full CLI. These tests capture CLI output
and compare it against a committed baseline (`tests/golden-tests-expected.log`).

**Running golden tests:**
```shell
./tests/run.sh    # Runs tests and compares output to expected baseline
```

**Updating the baseline when output changes intentionally:**
```shell
make update-golden
```

This is useful when:
- Adding new CLI features that produce different output
- Fixing bugs that change output format
- Adding new test cases to `golden-tests.sh`

The `run.sh` script:
1. Copies `tests/work-dir` to `tests/tmp-dir` for isolation
2. Runs `golden-tests.sh` in the temp directory
3. Normalizes output (removes timestamps, line numbers, etc.)
4. Compares against `golden-tests-expected.log`

**Adding new golden tests:**
1. Edit `tests/golden-tests.sh` to add new test commands
2. Run `make update-golden` to capture the new expected output
3. Review the diff in `tests/golden-tests-expected.log`
4. Commit both the script changes and the updated expected log

## IDE setup

If you use VSCode or a fork like Cursor or Windsurf, you can install the following
extensions:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

- [Based Pyright](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright)
  for type checking. Note that this extension works with non-Microsoft VSCode forks like
  Cursor.

## Publishing Releases

See [publishing.md](publishing.md) for instructions on publishing to PyPI.

## Documentation

- [uv docs](https://docs.astral.sh/uv/)

- [basedpyright docs](https://docs.basedpyright.com/latest/)

* * *

*This project uses [simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
