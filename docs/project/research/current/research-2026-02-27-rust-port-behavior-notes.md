# Research: repren Behavior Notes for Rust Port (2026-02-27)

## Purpose

Capture parity-critical runtime semantics from Python `repren` so Rust implementation
work can proceed from explicit behavior contracts.

## Scope

Focus areas:

1. simultaneous replacement engine
2. filesystem rewrite/rename lifecycle
3. traversal, backup handling, and undo/clean semantics
4. output and JSON contracts

## Replacement engine semantics

### Pattern parsing

1. Input format is tab-separated `regex<TAB>replacement` lines.
2. Blank lines and comment lines (`#` after optional leading whitespace) are ignored.
3. `--literal` escapes regex input with `re.escape`.
4. `--word-breaks` wraps each regex variant with `\b...\b`.
5. `--preserve-case` expands both regex and replacement into case variants:
- lowerCamel
- UpperCamel
- lower_underscore
- UPPER_UNDERSCORE
6. Duplicate `(regex, replacement)` pairs are deduplicated before compile.

### Matching and overlap policy

1. All matches for all patterns are collected before applying replacements.
2. Overlaps are resolved by sorted insertion:
- earlier-starting match wins
- later overlapping candidates are dropped
3. Replacements are applied simultaneously over original bytes (no cascading).

### Replacement expansion

1. Python `re` replacement expansion is used (`match.expand` semantics).
2. Capture references like `\1` work in replacement strings.
3. Behavior is byte-oriented for matching/replacement internals.

## Filesystem traversal and filtering semantics

### walk behavior

1. `walk_files` accepts explicit files and directories.
2. Include/exclude use `re.match` semantics on file/directory names (start-anchored).
3. During directory walk:
- directories matching exclude are pruned from descent
- files are filtered by include + exclude
4. Files ending with backup suffix (default `.orig`) or temp suffix
   (`.repren.tmp`) are always skipped for processing.
5. Return values:
- sorted file path list (deterministic order)
- count of skipped backup/temp files

### backup discovery

1. `find_backup_files` traverses similarly, but returns only files ending with backup suffix.
2. It also applies include/exclude filters to backup filenames.
3. Returned paths are sorted deterministically.

## Rewrite and rename lifecycle semantics

### transform_file behavior

1. For content transforms:
- write transformed content to `dest_path + temp_suffix`
- preserve source file permissions when creating temp output
- if `dry_run`, temp file is removed and no source mutation happens
2. Commit condition for content path:
- if `dest_path != source_path` OR `matches_found > 0`, then:
  - move source to backup (`source + backup_suffix`, clobber enabled)
  - move temp into destination (collision-safe move)
- else remove temp and leave source untouched
3. For rename-only (`do_contents == False`):
- if destination differs, source is moved to destination
- no backup file is created in rename-only mode

### rename collision behavior

1. Destination files are never clobbered when clobber is disabled.
2. Collision resolution appends numeric suffixes:
- `.1`, `.2`, ...
3. Existing numeric suffixes are normalized while probing, so repeated collisions
   continue incrementally.

## Undo and clean semantics

### undo_backups

For each backup file:

1. Strip backup suffix to derive original path.
2. Apply patterns to original path to predict renamed path.
3. Determine expected current target:
- original path (no rename case), or
- predicted renamed path
4. Skip with warning when:
- expected target path is missing
- backup mtime is newer than target mtime
5. Otherwise restore:
- move backup to original path
- remove predicted renamed file when it differs from original

Returns `(restored_count, skipped_count)`.

### clean_backups

1. Enumerates backups via `find_backup_files`.
2. Removes each backup unless dry-run.
3. Returns removal count.

## Output contracts

### Text mode (human)

1. Reports discovered file count and root paths processed.
2. Logs per-file `modify` and `rename` events.
3. Reports aggregate counts:
- files read/chars read
- matches found/overlaps skipped
- files changed, rewritten, renamed

### JSON mode

Current operation payloads:

1. `walk`:
- `operation`, `paths`, `files_found`, `skipped_backups`
2. `replace`:
- `operation`, `dry_run`, `patterns_count`, `files_found`, `chars_read`,
  `matches_found`, `matches_applied`, `files_changed`, `files_rewritten`, `files_renamed`
3. `undo`:
- `operation`, `dry_run`, `restored`, `skipped`
4. `clean_backups`:
- `operation`, `dry_run`, `removed`

## Parity constraints for Rust implementation

1. Keep overlap-drop and simultaneous replacement semantics exact.
2. Keep walk filtering and backup/temp skipping exact.
3. Keep collision suffix policy exact.
4. Keep backup/undo/clean state transitions and counters exact.
5. Keep JSON field names and operation tags stable.

## Related documents

- `docs/project/specs/active/plan-2026-02-27-rust-port-prep-and-test-hardening.md`
- `docs/project/research/current/research-2026-02-27-golden-harness-strategy.md`
- `../repren-rs/docs/project/specs/active/plan-2026-02-27-repren-port-master-plan.md`
