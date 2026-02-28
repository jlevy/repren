# Makefile for easy development workflows.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint format gendocs test test-golden test-golden-coverage update-golden upgrade build clean

default: install lint gendocs test

install:
	uv sync --all-extras

lint:
	uv run python devtools/lint.py

format:
	uvx flowmark@latest --inplace --smartquotes --ellipses docs/repren-docs.md repren/skills/SKILL.md

gendocs:
	uv run python devtools/gendocs.py

test:
	uv run pytest
	$(MAKE) test-golden-coverage
	$(MAKE) test-golden

test-golden:
	npx tryscript@latest run tests/tryscript/*.tryscript.md

test-golden-coverage:
	bash scripts/check-golden-coverage.sh

update-golden:
	npx tryscript@latest run --update tests/tryscript/*.tryscript.md

upgrade:
	uv sync --upgrade --all-extras --dev

build:
	uv build

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
