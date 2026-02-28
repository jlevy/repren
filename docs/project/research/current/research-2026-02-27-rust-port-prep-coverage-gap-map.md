# Research: repren Rust Port Prep Coverage Gap Map (2026-02-27)

## Purpose

Create a parity-risk-prioritized coverage gap map to guide Python prep work before
expanding Rust implementation.

Related spec:
- `docs/project/specs/active/plan-2026-02-27-rust-port-prep-and-test-hardening.md`

## Baseline measurements

Command run:

```bash
uv run pytest tests/pytests.py --cov=repren --cov-branch --cov-report=term-missing
```

Results:

| Module | Stmts | Miss | Branch | BrPart | Cover |
| --- | ---: | ---: | ---: | ---: | ---: |
| `repren/__init__.py` | 2 | 0 | 0 | 0 | 100% |
| `repren/claude_skill.py` | 61 | 25 | 6 | 1 | 61% |
| `repren/markdown_renderer.py` | 90 | 63 | 24 | 1 | 25% |
| `repren/repren.py` | 541 | 282 | 194 | 11 | 46% |
| **TOTAL** | **694** | **370** | **224** | **13** | **44%** |

Context checks:
- `82` pytest tests pass
- `./tests/run.sh` golden harness passes

## Risk-prioritized gap map

### P0 parity risk (must close early)

1. `repren/repren.py` mutation paths with low coverage:
- rewrite and rename path interactions
- backup creation and cleanup lifecycle
- undo restore behavior under edge conditions

2. error and conflict paths:
- invalid CLI argument combinations
- invalid regex/input handling paths
- operational filesystem errors

3. replacement core semantics:
- overlap precedence and nested match handling
- capturing-group replacement corner cases
- multiline behavior interactions (`--at-once`, `--dotall`)

### P1 parity risk (close during prep)

1. JSON output contracts:
- field consistency across modes and errors
- stable schema semantics for downstream automation

2. traversal/path edge cases:
- include/exclude edge patterns
- hidden/backup file interactions
- special-character path names

3. collision handling:
- deterministic rename-to-existing semantics
- numeric suffix behavior under repeated collisions

### P2 parity risk (can close in parallel)

1. `repren/claude_skill.py` and `repren/markdown_renderer.py` coverage:
- valuable for product quality, lower risk for core rename/replace parity

2. stress/performance scenarios:
- large files and large directory trees
- useful for robustness, not immediate parity blocker

## Concrete test additions mapped to issues

- `rpy-e82o` replacement/overlap tests
  - additional nested-overlap and tie-breaking cases
  - capture-group replacement edge cases
  - multiline replacement edge cases

- `rpy-wqj2` filesystem mutation tests
  - collision fan-out (`.1`, `.2`, repeated collisions)
  - move + backup + undo round-trip cases
  - backup suffix and invalid suffix scenarios

- `rpy-5jls` CLI conflict and JSON tests
  - incompatible flag combinations
  - required argument errors
  - json schema assertions for key modes and failures

## Readiness gate recommendation

Proceed to broad Rust implementation only after:

1. P0 items above have dedicated tests
2. full Python suite still passes
3. documented behavior notes are published for Rust implementation reference

## Notes

This analysis deliberately prioritizes behavioral confidence over raw coverage percentage.
The target is not only a higher number, but coverage of parity-critical semantics.

