# Plan Spec: repren Rust Port Prep and Test Hardening

## Purpose

Prepare the Python `repren` codebase to act as a high-fidelity specification for the
Rust port in `repren-rs`.

This plan focuses on test sufficiency, explicit behavior documentation, and parity-ready
artifacts that reduce ambiguity during Rust implementation.

## Background

A Rust port is underway in `../repren-rs` with `repos/repren` as source-of-truth.
Current Python tests pass, but coverage is not yet high enough to confidently treat the
suite as a complete behavioral specification.

Baseline measured on 2026-02-27:

- `uv run pytest tests/pytests.py --cov=repren --cov-branch --cov-report=term-missing`
  - Total coverage: `44%`
  - `repren/repren.py`: `46%`
- Golden harness: `./tests/run.sh` passes

Given repren's heavy filesystem mutation behavior, we need stronger coverage in error
paths, edge cases, and operation lifecycle semantics before Rust implementation expands.

## Summary of Task

Deliver a Python-side prep package for the Rust port:

1. Improve test coverage and behavior completeness in key parity-critical paths
2. Document exact semantics for replacement, rename, backup/undo/clean, and output modes
3. Decide and document golden test harness strategy (current shell harness vs migration)
4. Leave Python repo in a state where Rust parity tests can be written directly from
   Python artifacts

## Backward Compatibility

### Compatibility mode

- **Mode:** strict behavioral compatibility for existing CLI users
- New tests and docs should clarify behavior, not change it, unless a bug fix is
  explicitly approved

### Protected surfaces

- CLI flags and interactions
- Output and exit-code behavior relied on by scripts
- Backup, undo, and cleanup semantics
- JSON output schema

### Allowed changes

- Additional tests and fixtures
- Better documentation
- Test harness internal modernization if output behavior remains equivalent

## Stage 1: Planning Stage

### Scope boundaries

In scope:
- test additions
- parity behavior docs
- golden harness strategy and optional migration plan

Out of scope:
- major new runtime features
- broad refactors not tied to parity confidence

### Risk-focused priority list

1. Simultaneous replacement and overlap handling behavior
2. Filesystem mutation lifecycle (rewrite, rename, backups, undo, clean)
3. CLI conflict/error path behavior
4. JSON output contract stability

## Stage 2: Architecture Stage

### Existing assets to leverage

- `tests/pytests.py` already has strong seed coverage for many core behaviors
- `tests/golden-tests.sh` exercises full CLI workflows and has expected output baseline
- `tests/run.sh` normalization pipeline already controls some nondeterminism

### Required additions

- richer edge-case fixtures (unicode paths/content, malformed input cases)
- explicit behavior spec docs under `docs/project/`
- optional tryscript migration plan or rationale for retaining shell harness

## Stage 3: Refine Architecture

### Reuse opportunities

- Keep existing golden harness as baseline while adding targeted scenarios
- Reuse current fixture layout (`tests/work-dir`) for new edge-case scenarios
- Reuse unit test structure in `tests/pytests.py` classes for new focused cases

### Simplifications

- Do not split tests into many files right now; keep incremental additions in current
  structure unless maintainability clearly suffers
- Avoid harness migration and behavior changes in the same PR

## Stage 4: Implementation Plan

### Phase P1: Baseline and coverage analysis

- [x] record current uncovered branches/functions in `repren/repren.py`
- [x] prioritize uncovered logic by parity risk
- [x] add tracking notes in a new research/plan doc section

### Phase P2: Targeted unit/integration expansion

- [x] add tests for replacement overlap edge cases not currently covered
- [x] add tests for rename collision and directory move edge cases
- [x] add tests for backup suffix edge cases and invalid inputs
- [x] add tests for CLI invalid combinations and argument conflicts
- [x] add tests for JSON output fields in success and error workflows

### Phase P3: Filesystem edge-case coverage

- [ ] add read-only/permission error scenario tests where portable
- [ ] add path edge-case tests (spaces, special chars)
- [x] add regression tests for backup skip behavior during traversal

### Phase P4: Golden harness strategy

- [ ] document keep-vs-migrate decision for shell golden tests
- [ ] if migrating, produce phased migration plan preserving output normalization parity
- [ ] if not migrating now, document exact reasons and future trigger conditions

### Phase P5: Behavior documentation for Rust port

- [ ] write behavior notes for replacement engine semantics
- [ ] write behavior notes for filesystem mutation lifecycle
- [ ] write behavior notes for output modes and error model
- [ ] cross-link these notes to `repren-rs` master port plan

### Phase P6: Validation and handoff

- [ ] run full test suite (`make test` + golden harness)
- [ ] run coverage report and document delta vs baseline
- [ ] update active-spec status and summarize handoff checklist for Rust team

## Validation Plan

Automated:
- `uv run pytest tests/pytests.py --cov=repren --cov-branch --cov-report=term-missing`
- `./tests/run.sh`
- `make test`

Manual spot checks:
- verify representative JSON output samples against docs
- verify backup/undo/clean examples from docs against actual behavior

## Deliverables

- expanded Python test suite for parity-critical behaviors
- explicit behavior docs for Rust-port reference
- golden strategy decision doc (or migration plan)
- updated coverage metrics and gap summary

## Tracking

All implementation tasks from this spec are tracked as `tbd` issues in this repo
(prefix `rpy-*`), with dependency ordering from P1 to P6.

Initialized issue tree:

- Epic: `rpy-vrvt` Python prep for repren Rust port
- Tasks:
  - `rpy-32cl` P1 coverage gap audit
  - `rpy-e82o` P2 replacement/overlap tests
  - `rpy-wqj2` P3 filesystem mutation tests
  - `rpy-5jls` P4 CLI conflict + JSON tests
  - `rpy-ieaq` P5 golden harness strategy
  - `rpy-0nid` P6 behavior notes for Rust team
  - `rpy-v1fc` P7 final validation + handoff
