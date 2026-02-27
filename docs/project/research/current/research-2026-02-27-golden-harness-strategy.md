# Research: Golden Harness Strategy for Rust Port Prep (2026-02-27)

> Superseded (2026-02-27): This document captured a temporary keep-shell decision.
> The repository has since migrated to tryscript as the authoritative golden harness.
> See:
> `docs/project/specs/active/plan-2026-02-27-repren-python-tryscript-full-migration.md`.

## Purpose

Decide whether to keep the existing shell golden harness (`tests/golden-tests.sh` +
`tests/run.sh`) as the current parity baseline, or migrate immediately to a different
harness format before Rust parity work accelerates.

## Decision

Keep the shell golden harness as the authoritative baseline for now.

## Why keep it now

1. It already covers broad end-to-end CLI behavior:
- replacements, renames, full mode, include/exclude, `--walk-only`
- backup lifecycle (`--undo`, `--clean-backups`, custom backup suffix)
- JSON output mode and error paths
- skill install and collision handling scenarios

2. It is already normalized and deterministic in practice:
- `tests/run.sh` strips volatile paths/line numbers/timestamps
- baseline diffing is stable across reruns in this environment

3. Rust porting work benefits from stable fixtures immediately:
- changing the harness now would add migration noise unrelated to behavior parity
- current harness output can be consumed directly to build Rust parity checks

## Known limitations

1. Shell scripts are harder to refactor and parameterize than structured test fixtures.
2. Assertions are baseline-diff oriented, not strongly typed.
3. Running in parallel with other harness runs can create temp-dir collisions.

## Operational guidance for current harness

1. Run `./tests/run.sh` serially (do not run in parallel with pytest jobs that invoke it).
2. Treat `tests/golden-tests-expected.log` as a versioned contract artifact.
3. Update baseline only when behavior change is intentional and documented.

## Migration trigger conditions

Revisit migration only when one or more are true:

1. We need per-scenario selective execution to speed parity triage.
2. Golden diffs become too noisy for maintainable review.
3. Rust cross-language parity harness needs tighter, fixture-level assertions.

## Deferred migration plan sketch

If migration is needed later:

1. Keep shell harness as source of truth during transition.
2. Port one scenario group at a time into a structured harness.
3. Compare new harness output against existing baseline for each migrated group.
4. Only retire shell sections once parity and determinism are proven.

## Related documents

- `docs/project/specs/active/plan-2026-02-27-rust-port-prep-and-test-hardening.md`
- `../repren-rs/docs/project/specs/active/plan-2026-02-27-repren-port-master-plan.md`
