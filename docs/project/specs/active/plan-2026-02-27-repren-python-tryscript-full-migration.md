# Plan Spec: repren Python Full Tryscript Migration and Golden Discipline Hardening

## Purpose

Replace the legacy bash golden harness with a comprehensive, fixture-first tryscript
suite so the Python `repren` behavior contract is explicit, deterministic, and directly
portable to Rust parity tests.

## Background

State before this migration tranche (2026-02-27):

1. Golden coverage relied on:
   - `tests/golden-tests.sh`
   - `tests/run.sh`
   - `tests/golden-tests-expected.log`
2. CI and Make invoked shell harness directly.
3. Unit tests called the shell runner in an integration wrapper.
4. Scenario coverage was broad but monolithic and hard to evolve safely.

Reference sources used while designing migration:

1. `tbd guidelines golden-testing-guidelines`
2. `tbd shortcut checkout-third-party-repo` to clone:
   - `attic/blobsy` ([jlevy/blobsy](https://github.com/jlevy/blobsy))
3. Prior case-study implementation in:
   - `../flowmark-rs/repos/flowmark`

Patterns adopted from blobsy and flowmark:

1. root `tryscript.config.js` with deterministic env/path/patterns
2. modular scenario files by behavior domain
3. quality gate script enforcing anti-pattern and command/flag coverage checks
4. fixture-first test setup with per-suite isolated sandboxes

## Summary of Task

Deliver a full migration from bash golden tests to tryscript as the authoritative Python
CLI golden harness.

Target outcomes:

1. comprehensive tryscript modules under `tests/tryscript/`
2. fixture tree under `tests/tryscript/fixtures/`
3. root `tryscript.config.js`
4. `scripts/check-golden-coverage.sh`
5. Make/CI/pytest integration switched to tryscript
6. docs updated to remove shell-baseline workflow references

## Backward Compatibility

### Compatibility mode

- Strict CLI behavior compatibility for end users.
- Migration changes test harness structure, not product behavior.

### Protected surfaces

1. replacement/rename semantics
2. backup/undo/clean lifecycle
3. include/exclude walk behavior
4. JSON output structure
5. CLI help/error model and exit codes

### Allowed changes

1. golden harness layout and tooling
2. deterministic normalization and patternization
3. CI/test command wiring

## Stage 1: Planning Stage

### Scope

In scope:

1. replace shell harness with tryscript modules
2. enforce golden quality gates
3. document updated workflow

Out of scope:

1. intentional CLI behavior changes
2. unrelated runtime feature additions

### Acceptance criteria

1. `npx tryscript@latest run tests/tryscript/*.tryscript.md` passes
2. `bash scripts/check-golden-coverage.sh` passes
3. `make test` runs pytest + golden gates + tryscript
4. CI runs golden coverage gate + tryscript
5. unit/integration bridge test runs tryscript instead of shell runner

## Stage 2: Architecture Stage

### Target layout

1. `tests/tryscript/help-errors.tryscript.md`
2. `tests/tryscript/replacements.tryscript.md`
3. `tests/tryscript/renames-and-full.tryscript.md`
4. `tests/tryscript/patterns-and-case.tryscript.md`
5. `tests/tryscript/walk-and-filters.tryscript.md`
6. `tests/tryscript/backups-undo-clean.tryscript.md`
7. `tests/tryscript/json-output.tryscript.md`
8. `tests/tryscript/regex-wordbreaks.tryscript.md`
9. `tests/tryscript/fixtures/` (ported from legacy work-dir fixtures)
10. `tryscript.config.js`
11. `scripts/check-golden-coverage.sh`

### Determinism strategy

1. global env in tryscript config (`NO_COLOR=1`, `LC_ALL=C`)
2. fixed binary path (`$TRYSCRIPT_GIT_ROOT/.venv/bin`)
3. explicit version placeholder pattern (`[VERSION]`)
4. anti-pattern gate against bare `...` elisions

## Stage 3: Refine Architecture

### Why modular tryscript over shell monolith

1. per-domain diff review is much clearer
2. fixture setup is explicit per session
3. easier to add focused parity cases for Rust without destabilizing full baseline
4. no custom log-normalization pipeline required for typical repren outputs

### Port-to-Rust readiness impact

1. each tryscript module maps directly to a Rust parity test tranche
2. deterministic outputs simplify side-by-side Python vs Rust behavior checks
3. quality gate script keeps command/flag coverage from regressing during Rust bring-up

## Stage 4: Implementation Plan

### Phase G1: Spec and inventory

- [x] inventory legacy shell harness and entrypoints
- [x] review flowmark/blobsy golden discipline patterns
- [x] publish migration spec

### Phase G2: Build modular tryscript suite

- [x] create `tests/tryscript/fixtures/` from existing fixture corpus
- [x] author domain-split tryscript files for all major CLI behaviors
- [x] lock golden outputs with `tryscript --update`

### Phase G3: Add config and quality gates

- [x] add root `tryscript.config.js`
- [x] add `scripts/check-golden-coverage.sh`
- [x] enforce required-module and flag-coverage checks

### Phase G4: Switch wiring and validate

- [x] update Makefile targets (`test-golden`, `test-golden-coverage`, `update-golden`)
- [x] update CI workflow to run gate + tryscript
- [x] switch pytest integration wrapper to run tryscript
- [x] update developer docs and publishing checklist references
- [ ] remove or archive legacy shell harness artifacts (follow-up if retained temporarily)

## Validation Plan

Primary checks:

```bash
uv run pytest
bash scripts/check-golden-coverage.sh
npx tryscript@latest run tests/tryscript/*.tryscript.md
```

Secondary checks:

1. verify all major CLI option families appear in tryscript modules
2. verify quality gate fails when key modules/flags are removed
3. verify version output is patternized (`[VERSION]`) to avoid revision churn

## Deliverables

1. complete modular tryscript suite and fixtures
2. deterministic tryscript config
3. golden quality gate script
4. updated Make/CI/test integration wiring
5. updated documentation for golden workflow

## Tracking

`tbd` issue tree for this migration:

- Epic: `rpy-8woi`
- G1 spec/inventory: `rpy-dacv`
- G2 modular suite: `rpy-i8pi`
- G3 config/gates: `rpy-xxmw`
- G4 integration/validation: `rpy-i0xu`
