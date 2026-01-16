# Makefile for easy development workflows.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint format gendocs test update-golden upgrade build clean

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
	./tests/run.sh

update-golden:
	./tests/run.sh || cp tests/golden-tests-actual.log tests/golden-tests-expected.log

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
