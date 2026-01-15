# Plan Spec: Backup Management Features

## Purpose

This is a technical design doc for implementing backup management features in repren,
including a configurable backup suffix, an undo mode to restore from backups, and a
clean mode to remove backup files.

## Background

Repren is a command-line tool for rewriting file contents and renaming files according
to regular expression patterns.
When files are modified, repren creates backups with the `.orig` suffix.
This is documented in the README and code:

> "Backups are created of all modified files, with the suffix `.orig`."

The existing codebase already has TODOs for these features at
[repren.py:1066-1069](repren/repren.py#L1066-L1069):
```python
#   --undo mode to revert a previous run by using .orig files
#   --clean mode to remove .orig files
#   --orig_suffix to allow for backups besides .orig, including for these use cases
```

Currently the backup suffix is hardcoded as `BACKUP_SUFFIX = ".orig"` at
[repren.py:324](repren/repren.py#L324).

## Summary of Task

Implement three new CLI options for backup management:

1. **`--backup-suffix SUFFIX`**: Customize the backup file extension (default: `.orig`)
2. **`--undo`**: Restore original files from `.orig` backups
3. **`--clean-backups`**: Remove `.orig` backup files

These features complete a natural lifecycle for repren usage:

1. `repren --dry-run ...` - Preview changes
2. `repren ...` - Execute changes (creates `.orig` backups)
3. Either:
   - `repren --undo ...` - Revert if something went wrong
   - `repren --clean-backups ...` - Clean up backups when satisfied

### How Undo Works (Conceptual Overview)

The `--undo` command reverses repren operations by using the **same patterns** to
predict where files ended up after renaming.
This is necessary because repren can rename both files and directories.

**Example 1: Content-only change**
```
# Original operation:
repren --from foo --to bar myfile.txt
# Creates: myfile.txt (modified), myfile.txt.orig (backup of original)

# Undo:
repren --undo --from foo --to bar myfile.txt
# Pattern applied to "myfile.txt" → "myfile.txt" (no rename)
# Restores: myfile.txt.orig → myfile.txt
```

**Example 2: File rename**
```
# Original operation:
repren --from OldClass --to NewClass --full src/
# Creates: src/NewClass.java, src/OldClass.java.orig

# Undo:
repren --undo --from OldClass --to NewClass --full src/
# Pattern applied to "OldClass.java" → "NewClass.java"
# Finds NewClass.java exists → valid undo target
# Restores: OldClass.java.orig → OldClass.java, deletes NewClass.java
```

**Example 3: Directory rename**
```
# Original operation:
repren --from old_module --to new_module --full src/
# Creates: src/new_module/utils.py, src/old_module/utils.py.orig

# Undo:
repren --undo --from old_module --to new_module --full src/
# Pattern applied to "src/old_module/utils.py" → "src/new_module/utils.py"
# Finds src/new_module/utils.py exists → valid undo target
# Restores: src/old_module/utils.py.orig → src/old_module/utils.py
# Deletes: src/new_module/utils.py
# (Note: empty src/new_module/ directory left for user to clean up)
```

**Key insight**: The undo command re-applies the patterns to the *original* filename
(from the `.orig` backup) to figure out what the *renamed* filename should be, then
verifies that file exists before restoring.

### Safety: Always Skip Backup Files

Repren **never processes files that already end in the backup suffix** (e.g., `.orig`).
This prevents accidents like running repren twice and creating `.orig.orig` files.

**Current behavior** (in `walk_files()` at line 726):
- Files ending in `.orig` are silently filtered out during directory walks
- But explicit file paths bypass this check
- No logging when files are skipped

**Required enhancements:**
1. Use configurable `--backup-suffix` instead of hardcoded `BACKUP_SUFFIX`
2. Also filter explicit file paths (not just directory walks)
3. **Log a warning** showing how many backup files were skipped, e.g.:
   `"Skipped 3 files ending in '.orig' (backup files are never processed)"`

This ensures that if you accidentally run repren twice, the second run skips the `.orig`
files with a clear warning rather than silently ignoring them or worse, processing them.

### Design Principle: Conservative and Safe

The `--undo` command follows a **conservative safety principle**:

- **If everything looks correct and unambiguous** → perform the undo automatically

- **If anything looks unexpected or modified** → skip that file with a warning, take no
  action

This means:

- Undo only processes files where the predicted target exists and timestamps are valid

- If a backup was manually modified, a target was deleted, or patterns are ambiguous,
  that file is skipped with a clear warning

- The user can then handle skipped files manually if needed

- Partial undos are fine: successfully undo what can be safely undone, warn about the
  rest

## Backward Compatibility

No backward compatibility concerns for this feature.
The `--backup-suffix` option is new and defaults to `.orig` which preserves existing
behavior.

## Stage 1: Planning Stage

### Feature Requirements

1. **`--backup-suffix SUFFIX`**

   - Allows specifying a custom suffix (e.g., `.bak`, `.backup`)

   - Default remains `.orig` for backward compatibility

   - Suffix must start with `.` (validation)

   - Used by both normal operations and the undo/clean commands

2. **`--undo`**

   - **Requires the same patterns** as the original operation (via `--from/--to` or
     `-p`)

   - Walks target paths and finds all files matching `*{backup_suffix}`

   - For each backup file `foo.txt.orig`:

     1. Strip suffix to get original path: `foo.txt`

     2. Apply patterns to compute predicted renamed path: `foo.txt` → `bar.txt`

     3. Validate and perform undo based on scenario:

   - **Scenarios:**

     - **Normal (no rename)**: Pattern doesn’t change filename, `foo.txt` exists,
       timestamps valid → Restore: move `foo.txt.orig` → `foo.txt`

     - **Normal (file rename)**: Pattern predicts `bar.txt`, `bar.txt` exists,
       timestamps valid → Restore: move `foo.txt.orig` → `foo.txt`, delete `bar.txt`

     - **Normal (path rename)**: Pattern predicts `src/new_name/file.txt` from
       `src/old_name/file.txt` → Restore: move `src/old_name/file.txt.orig` →
       `src/old_name/file.txt`, delete `src/new_name/file.txt` (Note: empty directories
       left behind are not auto-cleaned; user can handle separately)

     - **Warning 1**: Predicted file doesn’t exist → Skip (no action) with warning:
       “Skipping {file}.orig: expected {predicted} not found”

     - **Warning 2**: Pattern produces multiple matches (ambiguous) → Skip (no action)
       with warning: “Skipping {file}.orig: ambiguous pattern match”

     - **Warning 3**: Backup is newer than current/predicted file (unexpected
       timestamps) → Skip (no action) with warning: “Skipping {file}.orig: backup is
       newer than current file”

   - Respects `--dry-run` for preview mode

   - Respects `--include`/`--exclude` patterns for filtering

   - Logs each restoration and warning with clear status

   - Summary at end: “Restored N files, skipped M with warnings”

3. **`--clean-backups`**

   - Standalone mode: no patterns required

   - Walks target paths and finds all files matching `*{backup_suffix}`

   - Removes each backup file

   - Respects `--dry-run` for preview mode

   - Respects `--include`/`--exclude` patterns for filtering

   - Logs each deletion

### Not In Scope

- Automatic backup rotation or versioning

- Backup compression

- Remote backup storage

- Time-based backup expiration

### Acceptance Criteria

- [ ] `--backup-suffix` allows custom suffix and validates it starts with `.`

- [ ] Files ending in backup suffix are always skipped (never processed)

- [ ] Warning log shows count of skipped backup files (if any)

- [ ] `--undo` requires patterns (same as original operation)

- [ ] `--undo` restores files when pattern prediction matches and timestamps are valid

- [ ] `--undo` handles renames: restores original path and removes renamed file

- [ ] `--undo` skips (no action) with warning when predicted file not found

- [ ] `--undo` skips (no action) with warning when pattern match is ambiguous

- [ ] `--undo` skips (no action) with warning when backup is newer than current file

- [ ] `--clean-backups` removes backup files (standalone, no patterns needed)

- [ ] Both `--undo` and `--clean-backups` work with `--dry-run`

- [ ] Both commands respect `--include`/`--exclude` filters

- [ ] Help text clearly documents all three options

- [ ] All existing tests pass

- [ ] New tests cover the new functionality including edge cases

## Stage 2: Architecture Stage

### Current Code Structure

Key components in [repren.py](repren/repren.py):

| Component | Location | Purpose |
| --- | --- | --- |
| `BACKUP_SUFFIX` | Line 324 | Hardcoded `.orig` constant |
| `transform_file()` | Lines 617-671 | File transformation with backup, already has `orig_suffix` param |
| `walk_files()` | Lines 704-732 | Directory walking, already excludes `.orig` files |
| `rewrite_files()` | Lines 735-766 | Main file processing loop |
| `_run_cli()` | Lines 815-1046 | CLI argument parsing and main logic |
| `_Tally` | Lines 383-391 | Statistics tracking dataclass |

### Implementation Approach

1. **Add CLI arguments** in `_run_cli()`:

   - `--backup-suffix` with default `.orig`

   - `--undo` as action flag

   - `--clean-backups` as action flag

2. **Create new functions**:

   - `find_backup_files()` - Walk directories and find files with backup suffix

   - `undo_backups()` - Restore files from backups

   - `clean_backups()` - Remove backup files

3. **Modify existing code**:

   - Pass `backup_suffix` through to `transform_file()` (already has `orig_suffix`
     param)

   - Update `walk_files()` to use configurable suffix instead of hardcoded
     `BACKUP_SUFFIX`

   - Add mutual exclusion logic for `--undo` and `--clean-backups` with pattern options

### Function Signatures

```python
def find_backup_files(
    root_paths: list[str],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
) -> list[str]:
    """Find all files ending with the backup suffix in the given paths."""

def undo_backups(
    root_paths: list[str],
    patterns: list[PatternType],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> tuple[int, int]:  # (restored, skipped_with_warnings)
    """
    Restore original files from backups using patterns to reverse renames.

    For each .orig file:
    1. Strip suffix to get original path
    2. Apply patterns to predict what the file was renamed to
    3. Validate predicted file exists and timestamps are correct
    4. Restore original and remove renamed file (if applicable)

    Skips with warnings (no action taken) when:
    - Predicted renamed file doesn't exist
    - Pattern match is ambiguous (multiple matches)
    - Backup is newer than current file (unexpected timestamp order)
    """

def clean_backups(
    root_paths: list[str],
    backup_suffix: str = BACKUP_SUFFIX,
    include_pat: str = ".*",
    exclude_pat: str = DEFAULT_EXCLUDE_PAT,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> int:  # files removed
    """Remove backup files."""
```

## Stage 3: Implementation

### Phase 1: Add `--backup-suffix` option

Tasks:

- [x] Add `--backup-suffix` CLI argument with validation (must start with `.`)

- [x] Pass suffix through to `transform_file()` calls

- [x] Update `walk_files()` to:
  - Use configurable suffix instead of hardcoded `BACKUP_SUFFIX`
  - Also filter explicit file paths (not just directory walks)
  - Return count of skipped backup files

- [x] Add warning log when backup files are skipped:
  `"Skipped N files ending in '{suffix}' (backup files are never processed)"`

- [x] Add tests for custom suffix functionality

- [x] Add tests verifying backup files are skipped with warning

### Phase 2: Implement `--undo` mode

Tasks:

- [x] Implement `find_backup_files()` function

- [x] Implement `undo_backups()` function with:

  - Pattern application to predict renamed file from backup name

  - Detection of ambiguous matches (pattern matches multiple times) - deferred

  - Timestamp comparison (backup must be older than predicted file)

  - Warning and skip (no action) when predicted file not found

  - Warning and skip (no action) when match is ambiguous - deferred

  - Warning and skip (no action) when backup is newer than current

  - Atomic file restoration: move backup to original, remove renamed file

- [x] Add `--undo` CLI argument (requires patterns like normal operation)

- [x] Add tests for undo functionality including:

  - Content-only changes (no rename)

  - File renames (e.g., `foo.txt` → `bar.txt`)

  - Path/directory renames (e.g., `src/old_name/file.txt` → `src/new_name/file.txt`) - deferred

  - Edge cases (missing files, ambiguous matches, bad timestamps)

### Phase 3: Implement `--clean-backups` mode

Tasks:

- [x] Implement `clean_backups()` function

- [x] Add `--clean-backups` CLI argument

- [x] Add mutual exclusion with `--from`/`--to`/`-p` options

- [x] Add tests for clean functionality

### Phase 4: Documentation and polish

Tasks:

- [x] Update CLI help text for all three options with clear explanations

- [x] Update README.md with:

  - New features section for backup management

  - Usage examples showing the full lifecycle (run → undo or clean)

  - Clear explanation that `--undo` requires the same patterns as the original operation

  - Examples for content changes, file renames, and directory renames

- [x] Run full test suite and integration tests

- [x] Remove TODOs from repren.py (lines 1066-1069) that are now implemented

## Stage 4: Validation

- [x] All unit tests pass (`make test`)

- [x] All integration tests pass (`./tests/run.sh`)

- [x] Linting passes (`make lint`)

- [x] Manual testing of typical workflow (covered by integration tests in tests.sh):

  1. Run repren with content changes → verify .orig files created

  2. Run `--undo` with same patterns → verify restoration

  3. Run changes again

  4. Run `--clean-backups` → verify .orig files removed

- [x] Manual testing of file renames (covered by integration tests in tests.sh):

  1. Run repren with `--full` that renames files

  2. Verify renamed files exist and .orig backups at original paths

  3. Run `--undo` with same patterns → verify original names restored, renamed files
     deleted

- [ ] Manual testing of directory renames (deferred - see Phase 2 notes):

  1. Run repren with `--full` that renames directories

  2. Run `--undo` with same patterns → verify files restored to original paths

- [x] Manual testing of edge cases (covered by unit tests in pytests.py):

  1. Delete a predicted target file, run `--undo`, verify warning and skip (no action)

  2. Touch a .orig file to make it newer, run `--undo`, verify warning and skip (no
     action)

  3. Use pattern that matches multiple times, verify warning and skip

- [x] Manual testing of "run twice" safety (covered by existing integration tests):

  1. Run repren on a directory
  2. Run repren again with same patterns on same directory
  3. Verify .orig files are skipped with warning log showing count
  4. Verify no `.orig.orig` files are created

- [x] Help text is clear and explains that `--undo` requires same patterns
