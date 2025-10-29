# Globbing and Backup Improvements Design

## Overview

This document describes the design for two major improvements to repren:
1. **Globbing Support**: Add modern glob pattern support with gitignore integration
2. **Backup Management**: Enhance control over `.orig` backup files

## 1. Globbing Support

### Goals

- Support standard glob patterns (e.g., `*.md`, `docs/**/*.md`)
- Use modern globbing practices compatible with common tools
- Respect `.gitignore` files by default
- Allow users to opt out of gitignore filtering with `--noignore` flag

### Design

#### Core Implementation

We will extend the file discovery mechanism in `walk_files()` to support:

1. **Glob Pattern Expansion**: Use Python's `glob` module or `pathlib.Path.glob()` for pattern matching
2. **Gitignore Integration**: Use the `pathspec` library (specifically `pathspec.gitignore.GitIgnoreSpec`) to filter files

#### Key Components

```python
class GitignoreFilter:
    """Handles gitignore-based file filtering."""

    def __init__(self, base_path: str):
        """Initialize filter by finding and parsing .gitignore files."""
        self.base_path = base_path
        self.specs = self._load_gitignore_specs()

    def _load_gitignore_specs(self) -> List[GitIgnoreSpec]:
        """Walk up from base_path and load all .gitignore files."""
        # Returns list of GitIgnoreSpec objects for hierarchical checking
        pass

    def should_ignore(self, path: str) -> bool:
        """Check if path should be ignored based on gitignore rules."""
        # Check path against all loaded specs
        pass
```

```python
def expand_globs(
    patterns: List[str],
    respect_gitignore: bool = True
) -> List[str]:
    """
    Expand glob patterns to file paths.

    Args:
        patterns: List of glob patterns or file paths
        respect_gitignore: If True, filter out gitignored files

    Returns:
        List of matching file paths
    """
    pass
```

#### Integration Points

- **Command-line arguments**: Accept glob patterns in `root_paths`
- **File walking**: Modify `walk_files()` to:
  - Detect glob patterns (contains `*`, `?`, `[`, or `**`)
  - Expand patterns using glob matching
  - Apply gitignore filtering when enabled
  - Fall back to current behavior for regular paths

#### New Command-line Option

- `--noignore`: Disable gitignore filtering (default: False, meaning gitignore is respected)

### Examples

```bash
# Process all markdown files
repren --from foo --to bar '*.md'

# Process markdown files in docs directory recursively
repren --from foo --to bar 'docs/**/*.md'

# Process files but ignore .gitignore rules
repren --from foo --to bar --noignore '*.py'

# Mix glob patterns and regular paths
repren --from foo --to bar 'src/**/*.py' tests/test_specific.py
```

### Edge Cases

1. **No matches**: If a glob pattern matches no files, log a warning
2. **Gitignore precedence**: Respect `.gitignore` files at all directory levels
3. **Always ignored**: Continue to always ignore `.orig` and `.repren.tmp` files
4. **Pattern vs path**: Auto-detect glob patterns vs regular paths

## 2. Backup Management

### Goals

- Allow users to disable backup file creation
- Provide utility to clean up existing `.orig` files
- Maintain safety with dry-run compatibility

### Design

#### New Command-line Options

1. **`--nobackup`**: Disable creation of `.orig` backup files
   - When enabled, modified files won't create backups
   - Still uses temp files for atomic operations
   - Incompatible with safety-conscious workflows but useful for version-controlled projects

2. **`--rm-backups [DIR]`**: Remove all `.orig` files in specified directory
   - Recursively finds and removes `.orig` files
   - Compatible with `-n/--dry-run` for preview
   - If DIR not specified, uses current directory

#### Implementation

```python
def transform_file(
    transform: Optional[TransformFunc],
    source_path: str,
    dest_path: str,
    orig_suffix: str = BACKUP_SUFFIX,
    temp_suffix: str = TEMP_SUFFIX,
    by_line: bool = False,
    dry_run: bool = False,
    create_backup: bool = True,  # NEW PARAMETER
) -> _MatchCounts:
    """
    Transform file with optional backup creation.

    Args:
        create_backup: If False, skip creating .orig backup files
    """
    # Modify to only create backup if create_backup=True
    pass
```

```python
def remove_backups(
    root_path: str,
    dry_run: bool = False,
    log: LogFunc = no_log,
) -> int:
    """
    Remove all .orig backup files in directory tree.

    Args:
        root_path: Root directory to search
        dry_run: If True, only log what would be removed
        log: Logging function

    Returns:
        Number of files removed (or that would be removed in dry-run)
    """
    pass
```

#### Integration Points

- **Option parsing**: Add `--nobackup` flag and `--rm-backups` action
- **File transformation**: Pass `create_backup` parameter through call chain
- **Special mode**: `--rm-backups` runs before other operations or as standalone

### Examples

```bash
# Rewrite files without creating backups (use with caution!)
repren --from foo --to bar --nobackup src/

# Preview backup removal
repren --rm-backups -n src/

# Actually remove backups
repren --rm-backups src/

# Combine with other operations (backups removed first)
repren --rm-backups --from foo --to bar src/
```

### Safety Considerations

1. **`--nobackup` warnings**: Log warning that backups are disabled
2. **Dry-run support**: Both features support `-n` for preview
3. **Clear messaging**: Show count of backups that will be/were removed
4. **Git integration**: Document that these features work well with git-tracked projects

## Testing Strategy

### Globbing Tests

1. **Pattern expansion**:
   - Test `*.ext` patterns
   - Test `**/*.ext` recursive patterns
   - Test character classes `[abc]` and ranges `[0-9]`
   - Test multiple patterns

2. **Gitignore integration**:
   - Test basic gitignore patterns
   - Test directory-level .gitignore files
   - Test nested .gitignore files
   - Test `--noignore` flag
   - Test that .orig files are always ignored

3. **Edge cases**:
   - Empty results
   - No .gitignore present
   - Malformed patterns

### Backup Management Tests

1. **`--nobackup` flag**:
   - Verify no .orig files created
   - Verify temp files still used
   - Verify actual file changes applied
   - Test with `-n` dry-run

2. **`--rm-backups`**:
   - Verify .orig files removed
   - Verify other files untouched
   - Test dry-run mode
   - Test recursive removal
   - Test with no backups present

3. **Integration**:
   - Test combining `--rm-backups` with replacements
   - Test error handling

## Dependencies

- **pathspec**: For gitignore support
  - Add to `pyproject.toml` dependencies
  - Well-maintained library with good gitignore spec compliance

## Implementation Plan

1. Add `pathspec` dependency to `pyproject.toml`
2. Implement gitignore filtering utilities
3. Extend `walk_files()` to support glob patterns
4. Add `--noignore` command-line option
5. Implement backup management functions
6. Add `--nobackup` and `--rm-backups` options
7. Write comprehensive tests for all features
8. Update documentation and examples

## Backward Compatibility

- All changes are backward compatible
- Existing regex-based `--include` and `--exclude` continue to work
- Glob patterns are auto-detected, so no breaking changes to existing usage
- Default behavior (creating backups, respecting gitignore) can be explicitly overridden
