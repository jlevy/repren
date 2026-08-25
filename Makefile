# Makefile for easy development workflows.
# See docs/development.md for docs.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

# Use only the checked-in project configuration. Otherwise uv merges user- and
# system-level settings into uv.lock, which can make it fail on another machine.
UV_CONFIG_FILE := $(CURDIR)/uv.toml
export UV_CONFIG_FILE

# Safe default for every dependency resolution invoked through this Makefile.
UV_EXCLUDE_NEWER ?= 14 days
export UV_EXCLUDE_NEWER

# Pin standalone developer tools that are not part of the uv lockfile.
FLOWMARK := uvx --from flowmark-rs==0.3.2 flowmark
TRYSCRIPT := npx --no-install tryscript

.PHONY: default install install-hooks lint lint-check format format-check gendocs gendocs-check test test-golden test-golden-coverage update-golden upgrade build clean

default: install lint gendocs test

install:
	uv sync --all-extras --all-groups
	npm ci --ignore-scripts

install-hooks:
	@current="$$(git config --get core.hooksPath || true)"; \
	if [ -n "$$current" ] && [ "$$current" != ".githooks" ]; then \
		echo "Refusing to replace existing core.hooksPath: $$current" >&2; \
		exit 1; \
	fi
	git config --worktree core.hooksPath .githooks

lint:
	uv run python devtools/lint.py

# Check-only lint, matching CI (does not modify files).
lint-check:
	uv run python devtools/lint.py --check

format:
	$(FLOWMARK) --auto .
	$(MAKE) gendocs

format-check:
	$(FLOWMARK) --auto --check .

gendocs:
	uv run python devtools/gendocs.py

gendocs-check:
	uv run python devtools/gendocs.py
	git diff --exit-code -- README.md repren/repren.py

test:
	uv run pytest
	$(MAKE) test-golden-coverage
	$(MAKE) test-golden

test-golden:
	$(TRYSCRIPT) run tests/tryscript/*.tryscript.md

test-golden-coverage:
	bash scripts/check-golden-coverage.sh

update-golden:
	$(TRYSCRIPT) run --update tests/tryscript/*.tryscript.md

upgrade:
	uv sync --upgrade --all-extras --all-groups

build: install
	uv build --no-build-isolation

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .ruff_cache/
	-rm -rf .mypy_cache/
	-rm -rf node_modules/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
