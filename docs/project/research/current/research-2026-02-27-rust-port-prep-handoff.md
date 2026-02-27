# Research: Rust Port Prep Handoff (2026-02-27)

## Purpose

Summarize Python-side prep completion status, validation results, and handoff artifacts
for the Rust implementation team in `repren-rs`.

## Baseline vs current

### Baseline (2026-02-27 start)

1. `82` pytest tests passing
2. Coverage:
- `TOTAL`: `44%`
- `repren/repren.py`: `46%`

### Current (2026-02-27 handoff)

1. `98` pytest tests passing
2. Coverage:
- `TOTAL`: `52%`
- `repren/repren.py`: `55%`
3. Golden harness (`./tests/run.sh`) passes

## Commands run

```bash
make test
uv run pytest tests/pytests.py
uv run pytest tests/pytests.py --cov=repren --cov-branch --cov-report=term-missing
./tests/run.sh
```

## What was added

### Tests

Expanded `tests/pytests.py` with parity-critical checks for:

1. pattern parsing edge behavior
2. overlap and replacement semantics
3. backup/temp skip behavior in traversal
4. backup discovery + undo + clean lifecycle
5. CLI conflict/error paths and JSON output fields
6. path edge cases (spaces/special characters/unicode rename path)

### Behavior docs

1. `docs/project/research/current/research-2026-02-27-rust-port-behavior-notes.md`
2. `docs/project/research/current/research-2026-02-27-golden-harness-strategy.md`

## Handoff checklist for Rust implementation

1. Use Python tests plus behavior notes as the parity contract.
2. Match JSON schema keys and operation names exactly.
3. Match rename collision suffix semantics (`.1`, `.2`, ...).
4. Match traversal include/exclude and backup/temp skip behavior.
5. Match undo skip rules (missing target, backup newer than target).
6. Preserve shell golden baseline as regression contract while Rust parity harness grows.

## Open prep limitations

1. Permission-error branch testing remains limited due cross-platform portability concerns.
2. `claude_skill.py` and `markdown_renderer.py` remain lower-coverage areas and are not
   core blockers for `repren.py` parity work.

## Related documents

1. `docs/project/specs/active/plan-2026-02-27-rust-port-prep-and-test-hardening.md`
2. `docs/project/research/current/research-2026-02-27-rust-port-prep-coverage-gap-map.md`
3. `../repren-rs/docs/project/specs/active/plan-2026-02-27-repren-port-master-plan.md`
