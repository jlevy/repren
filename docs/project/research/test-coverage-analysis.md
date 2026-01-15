# Test Coverage Analysis

## Current Test Architecture

The codebase uses **two complementary test approaches**:

### 1. Golden Tests (`tests/tests.sh` → `tests/tests-expected.log`)

Shell-based integration tests that capture CLI output and compare against expected results. This approach is excellent for:
- Testing actual user-facing behavior
- Catching regressions in output format
- Validating end-to-end workflows
- Documenting expected behavior through examples

### 2. Unit Tests (`tests/pytests.py`)

Python unit tests for internal functions. Current coverage: **50%** (458 statements, 227 missed)

---

## Golden Test Coverage Matrix

| Feature | Tested | Commands/Patterns Used |
|---------|--------|------------------------|
| **Basic replacement** | ✅ | `--from Humpty --to Dumpty` |
| **Dry run** | ✅ | `-n` |
| **Case sensitive** | ✅ | `--from humpty` (no match for `Humpty`) |
| **Case insensitive** | ✅ | `-i` |
| **File renames only** | ✅ | `--renames` |
| **Full mode** | ✅ | `--full` (renames + contents) |
| **Pattern files** | ✅ | `-p patterns-misc` |
| **Preserve case** | ✅ | `--preserve-case -p patterns-rotate-abc` |
| **Word breaks** | ✅ | `--word-breaks` |
| **Include filter** | ✅ | `--include='.*[.]txt$'` |
| **Exclude filter** | ✅ | `--exclude='beech\|maple'` |
| **Walk-only** | ✅ | `--walk-only` |
| **Backup undo** | ✅ | `--undo` |
| **Backup clean** | ✅ | `--clean-backups` |
| **Custom backup suffix** | ✅ | `--backup-suffix .bak` |
| **Backup skip behavior** | ✅ | (implicitly via `.orig` files in output) |
| **Overlap counting** | ✅ | (shown in output stats) |
| **Regex patterns** | ❌ | Not tested |
| **Capturing groups** | ❌ | Not tested |
| **Literal mode** | ❌ | `--literal` |
| **Dotall mode** | ❌ | `--dotall` |
| **At-once mode** | ❌ | `--at-once` |
| **Parse-only** | ❌ | `-t` / `--parse-only` |
| **Stdin/stdout** | ❌ | Piped input |
| **Quiet mode** | ❌ | `-q` |
| **Moving files** | ❌ | (noted as TODO in tests.sh) |
| **File collisions** | ❌ | Rename to existing name |
| **Error cases** | ❌ | Invalid patterns, permissions |

---

## Proposed Golden Test Enhancements

### Phase 1: Add Missing CLI Flags

Add these sections to `tests.sh`:

```bash
# --- Regex and capturing groups ---

cp -a original test-regex

# Create a pattern file with capturing group
echo 'figure ([0-9]+)	Figure \1' > patterns-capturing
run -p patterns-capturing test-regex/...

# Verify back-reference works
run --from '(\w+)@(\w+)' --to '\2-\1' test-regex/...


# --- Literal mode ---

cp -a original test-literal

# Without --literal: . matches any char
run --from 'foo.bar' --to 'REPLACED' test-literal/...

# With --literal: . matches only literal .
cp -a original test-literal2
run --literal --from 'foo.bar' --to 'REPLACED' test-literal2/...


# --- At-once mode (multiline patterns) ---

cp -a original test-atonce

# Create multiline test file
printf 'start\nmiddle\nend' > test-atonce/multiline.txt

# Default (line-by-line) won't match across lines
run --from 'start.*end' --to 'REPLACED' test-atonce/multiline.txt

# With --at-once, pattern spans lines
cp -a original test-atonce2
run --at-once --from 'start.*end' --to 'REPLACED' test-atonce2/multiline.txt


# --- Dotall mode ---

cp -a original test-dotall

# Without dotall: . doesn't match newline
run --at-once --from 'start.middle' --to 'REPLACED' test-dotall/...

# With dotall: . matches newline
run --at-once --dotall --from 'start.middle' --to 'REPLACED' test-dotall/...


# --- Parse-only mode ---

run -t --from 'foo' --to 'bar'
run -t -p patterns-misc


# --- Stdin/stdout mode ---

echo 'foo bar foo' | run --from foo --to bar
echo -e 'line1\nline2' | run --from 'line([0-9])' --to 'LINE \1'


# --- Quiet mode ---

cp -a original test-quiet
run -q --from Humpty --to Dumpty test-quiet/humpty-dumpty.txt
# Should have no output but still make changes
diff original/humpty-dumpty.txt test-quiet/humpty-dumpty.txt || expect_error


# --- File collision handling ---

cp -a original test-collision
touch test-collision/dumpty-dumpty.txt  # Pre-existing target
run --renames --from humpty --to dumpty test-collision
ls_portable test-collision  # Should show dumpty-dumpty.txt.1 or similar


# --- Error cases ---

run --from '[invalid(regex' --to 'bar' original || expect_error
run --from '' --to 'bar' original || expect_error
```

### Phase 2: Add Test Input Files

Create additional files in `tests/work-dir/original/`:

1. **`patterns-capturing`** - Pattern file with regex capturing groups
2. **`patterns-multiline`** - Patterns that span multiple lines
3. **`file-with-dots.txt`** - File containing literal dots for `--literal` testing
4. **`multiline.txt`** - Multi-line content for `--at-once` testing
5. **`binary-file.bin`** - Binary content to verify binary handling

### Phase 3: Track Test Coverage in Pattern File

Create a central registry of what's tested. Add to `tests/work-dir/`:

```
# tests/work-dir/test-coverage-matrix.md

| Pattern/Command | Test Case | Line in tests.sh |
|-----------------|-----------|------------------|
| --from/--to     | Basic     | 42               |
| -i              | Case insensitive | 80        |
| \1 back-ref     | Capturing groups | TODO     |
| --literal       | Escape regex | TODO          |
...
```

---

## Unit Test Gaps (pytests.py)

The golden tests cover CLI behavior well, but some internal functions lack direct unit tests:

### Functions Needing Unit Tests

| Function | Current Coverage | Priority |
|----------|------------------|----------|
| `multi_replace()` | Indirect only | High |
| `_sort_drop_overlaps()` | Not tested | High |
| `transform_stream()` | Not tested | Medium |
| `transform_file()` | Not tested | Medium |
| `move_file()` | Not tested | Medium |
| `make_parent_dirs()` | Not tested | Low |

### Recommended Additions to pytests.py

```python
class TestMultiReplace:
    """Direct tests for multi_replace function."""

    def test_single_pattern(self):
        patterns = [(_compile("foo"), "bar")]
        result, count = multi_replace(patterns, "foo baz foo")
        assert result == "bar baz bar"
        assert count == 2

    def test_multiple_patterns_no_overlap(self):
        patterns = [(_compile("foo"), "FOO"), (_compile("bar"), "BAR")]
        result, count = multi_replace(patterns, "foo bar")
        assert result == "FOO BAR"
        assert count == 2

    def test_overlapping_patterns(self):
        """When patterns overlap, first match wins."""
        patterns = [(_compile("foobar"), "LONG"), (_compile("foo"), "SHORT")]
        result, count = multi_replace(patterns, "foobar")
        assert result == "LONG"  # Not "SHORTbar"


class TestSortDropOverlaps:
    """Test overlap detection and resolution."""

    def test_no_overlaps(self):
        matches = [(0, 3, "foo"), (4, 7, "bar")]
        result = _sort_drop_overlaps(matches)
        assert len(result) == 2

    def test_nested_overlap(self):
        matches = [(0, 10, "long"), (2, 5, "short")]
        result = _sort_drop_overlaps(matches)
        assert len(result) == 1
        assert result[0][2] == "long"  # First match wins


class TestTransformStream:
    """Test stream transformation with different modes."""

    def test_line_by_line_mode(self):
        """Default mode doesn't match across lines."""

    def test_at_once_mode(self):
        """At-once mode matches across lines."""
```

---

## Summary

### Golden Tests (Primary - Extend First)
The shell-based golden tests are the **most valuable** for a CLI tool like repren. They:
- Test actual user behavior
- Are easy to extend (just add commands)
- Serve as documentation
- Catch output format regressions

**Recommended additions:**
1. Regex/capturing groups
2. `--literal`, `--dotall`, `--at-once` flags
3. Stdin/stdout piping
4. `-t` parse-only mode
5. `-q` quiet mode
6. File collision handling
7. Error cases

### Unit Tests (Secondary - Targeted Additions)
Add unit tests for:
1. `multi_replace()` with edge cases
2. `_sort_drop_overlaps()` overlap handling
3. Error paths in `parse_patterns()`

### Test Tracking
Consider adding a test coverage matrix to `tests/work-dir/` that maps features → test cases for easier tracking of what's covered.
