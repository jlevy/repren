# Test Coverage Analysis

## Current State

**Overall coverage: 50%** (458 statements, 227 missed)

### What's Well Tested

The current test suite has good coverage of:

1. **Case conversion functions** - `to_lower_camel`, `to_upper_camel`, `to_lower_underscore`, `to_upper_underscore` with extensive Unicode test cases
2. **Name splitting** - `_split_name` with CamelCase and underscore-separated names
3. **Backup management functions** - `find_backup_files`, `undo_backups`, `clean_backups` have dedicated test classes
4. **`walk_files`** - Backup suffix filtering is well tested
5. **CLI validation** - Tests for `--backup-suffix`, `--undo`, `--clean-backups` argument validation
6. **Integration tests** - Shell-based tests (`tests.sh`) cover common workflows including:
   - Basic `--from`/`--to` replacements
   - Dry run mode (`-n`)
   - File renames (`--renames`)
   - Full mode (`--full`)
   - Case insensitive matching (`-i`)
   - Pattern files (`-p`)
   - Case preservation (`--preserve-case`)
   - Word breaks (`--word-breaks`)
   - Include/exclude patterns

---

## Coverage Gaps (Priority Order)

### High Priority - Core Functionality

#### 1. Regex Features and Capturing Groups
**Lines affected:** Pattern matching/replacement logic
**Current state:** No unit tests for regex back-references (`\1`, `\2`)
**Recommended tests:**
```python
def test_capturing_groups():
    """Test regex capturing groups and back-references."""
    patterns = parse_patterns(r"figure ([0-9]+)\tFigure \1")
    # Test replacement preserves captured group

def test_nested_capturing_groups():
    """Test multiple and nested capturing groups."""
    patterns = parse_patterns(r"(\w+)\.(\w+)\t\2_\1")
```

#### 2. Overlapping Pattern Handling
**Lines affected:** `_sort_drop_overlaps` (416, 430-437, 439-446)
**Current state:** Logic exists but no dedicated tests
**Recommended tests:**
```python
def test_overlapping_patterns_first_wins():
    """When two patterns overlap, the first pattern in file wins."""

def test_nested_pattern_overlap():
    """A shorter pattern inside a longer one."""

def test_adjacent_non_overlapping():
    """Adjacent matches that don't overlap both apply."""
```

#### 3. Multi-replace Core Function
**Lines affected:** `multi_replace` (469-500)
**Current state:** Tested indirectly through integration tests only
**Recommended tests:**
```python
def test_multi_replace_basic():
    """Direct test of multi_replace function."""

def test_multi_replace_multiple_patterns():
    """Multiple patterns applied simultaneously."""

def test_multi_replace_no_match():
    """No matches returns original content unchanged."""
```

#### 4. Stream/Stdin Mode
**Lines affected:** 1287-1298
**Current state:** No tests for stdin/stdout piping
**Recommended tests:**
```python
def test_stdin_to_stdout():
    """Test reading from stdin and writing to stdout."""
    result = subprocess.run(
        ["uv", "run", "repren", "--from", "foo", "--to", "bar"],
        input="foo bar foo",
        capture_output=True,
        text=True
    )
    assert result.stdout == "bar bar bar"
```

### Medium Priority - Options and Modes

#### 5. At-Once vs Line-by-Line Mode
**Lines affected:** `transform_stream` (615-630), `--at-once` flag
**Current state:** No explicit tests comparing the modes
**Recommended tests:**
```python
def test_at_once_multiline_pattern():
    """--at-once allows patterns to span multiple lines."""

def test_line_by_line_default():
    """Default mode processes line by line."""
```

#### 6. Literal Mode
**Lines affected:** `--literal` flag in `parse_patterns`
**Current state:** Not tested
**Recommended tests:**
```python
def test_literal_mode_escapes_regex():
    """--literal should escape regex special characters."""
    # Pattern like "foo.bar" should match literal "foo.bar" not "fooxbar"
```

#### 7. Dotall Mode
**Lines affected:** `--dotall` flag
**Current state:** Not tested
**Recommended tests:**
```python
def test_dotall_matches_newlines():
    """--dotall allows . to match newline characters."""
```

#### 8. Parse-Only Mode
**Lines affected:** `--parse-only` / `-t` (lines 1242-1243)
**Current state:** Not tested
**Recommended tests:**
```python
def test_parse_only_shows_patterns():
    """--parse-only displays parsed patterns without processing files."""
```

### Medium Priority - File Operations

#### 9. File Collision Handling
**Lines affected:** `move_file` (594-603)
**Current state:** Not tested
**Recommended tests:**
```python
def test_rename_collision_adds_numeric_suffix():
    """When renamed file exists, add .1, .2, etc."""

def test_multiple_files_same_destination():
    """Multiple files renamed to same name get distinct suffixes."""
```

#### 10. Directory Creation on Rename
**Lines affected:** `make_parent_dirs` (586-587)
**Current state:** Not tested
**Recommended tests:**
```python
def test_rename_creates_parent_directories():
    """Renaming to nested path creates necessary directories."""
    # Pattern: "file.txt" -> "new/nested/dir/file.txt"
```

#### 11. Permission Preservation
**Lines affected:** `transform_file` (658)
**Current state:** Not tested
**Recommended tests:**
```python
def test_file_permissions_preserved():
    """Modified files retain original permissions."""
    # Create file with 0o755, modify it, verify permissions unchanged
```

### Lower Priority - Edge Cases

#### 12. Binary File Handling
**Lines affected:** Bytes-based operations throughout
**Current state:** Not tested
**Recommended tests:**
```python
def test_binary_file_replacement():
    """Tool correctly handles binary files with byte patterns."""

def test_mixed_encoding_file():
    """Files with non-UTF-8 content are processed correctly."""
```

#### 13. Empty Files
**Current state:** Not tested
**Recommended tests:**
```python
def test_empty_file_processing():
    """Empty files are processed without error."""
```

#### 14. Symlink Handling
**Current state:** Not tested, behavior unclear
**Recommended tests:**
```python
def test_symlink_to_file():
    """Symlinks to files - should they follow or modify the link?"""
```

#### 15. Large File Performance
**Current state:** Not tested
**Recommended tests:**
```python
def test_large_file_memory_usage():
    """Processing large files doesn't exhaust memory in line mode."""
```

---

## Error Handling Gaps

### 16. Invalid Pattern File
**Lines affected:** `parse_patterns` (994-995)
**Recommended tests:**
```python
def test_invalid_pattern_format():
    """Pattern without tab separator should raise error."""

def test_invalid_regex_pattern():
    """Invalid regex syntax should raise error with helpful message."""
```

### 17. File Access Errors
**Lines affected:** File operations throughout
**Recommended tests:**
```python
def test_unreadable_file_error():
    """Appropriate error when file cannot be read."""

def test_unwritable_destination_error():
    """Appropriate error when destination is not writable."""
```

### 18. Interrupted Processing
**Lines affected:** Temp file cleanup logic
**Recommended tests:**
```python
def test_temp_files_cleaned_on_error():
    """Temporary files don't accumulate on processing errors."""
```

---

## Test Infrastructure Improvements

### Recommended Changes

1. **Add pytest-cov to dev dependencies** - ✅ Done (added during this analysis)

2. **Add coverage threshold to CI** - Fail builds if coverage drops below baseline
   ```toml
   # pyproject.toml
   [tool.coverage.run]
   branch = true

   [tool.coverage.report]
   fail_under = 50  # Increase as coverage improves
   ```

3. **Separate unit tests from integration tests** - Consider splitting `pytests.py` into:
   - `tests/unit/test_patterns.py` - Pattern parsing and matching
   - `tests/unit/test_case_conversion.py` - Case utilities
   - `tests/unit/test_file_operations.py` - File handling
   - `tests/integration/test_cli.py` - CLI argument handling
   - `tests/integration/test_workflows.py` - End-to-end workflows

4. **Add property-based testing** - Consider using Hypothesis for:
   - Pattern matching edge cases
   - Case conversion roundtrips
   - File path transformations

---

## Implementation Priority

### Phase 1 - Quick Wins (Est. effort: Low)
- [ ] Stdin/stdout mode tests
- [ ] Literal mode tests
- [ ] Parse-only mode tests
- [ ] Empty file tests

### Phase 2 - Core Coverage (Est. effort: Medium)
- [ ] Capturing groups and back-references
- [ ] Overlapping pattern tests
- [ ] Multi-replace unit tests
- [ ] At-once vs line-by-line mode

### Phase 3 - File Operations (Est. effort: Medium)
- [ ] File collision handling
- [ ] Directory creation on rename
- [ ] Permission preservation
- [ ] Binary file handling

### Phase 4 - Edge Cases and Errors (Est. effort: Higher)
- [ ] Error handling paths
- [ ] Large file testing
- [ ] Symlink behavior
- [ ] Interrupted processing cleanup

---

## Summary

The codebase has solid integration test coverage for common workflows via the shell tests, but lacks:
- **Unit tests for core functions** (multi_replace, transform operations)
- **Regex feature tests** (capturing groups, special modes)
- **Edge case coverage** (collisions, errors, binary files)
- **Error path testing** (invalid inputs, access errors)

Improving test coverage in these areas would:
1. Catch regressions more reliably
2. Document expected behavior for edge cases
3. Make the codebase safer for refactoring
4. Increase confidence for new contributors
