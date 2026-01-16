# Test Coverage Analysis

## Current Test Architecture

The codebase uses **two complementary test approaches**:

### 1. Golden Tests (`tests/golden-tests.sh` → `tests/golden-tests-expected.log`)

Shell-based integration tests that capture CLI output and compare against expected
results. This approach is excellent for:
- Testing actual user-facing behavior
- Catching regressions in output format
- Validating end-to-end workflows
- Documenting expected behavior through examples

### 2. Unit Tests (`tests/pytests.py`)

Python unit tests for internal functions.
Current coverage: **40%** (586 statements, 351 missed)

* * *

## Golden Test Coverage Matrix

| Feature | Tested | Commands/Patterns Used |
| --- | --- | --- |
| **Basic replacement** | ✅ | `--from Humpty --to Dumpty` |
| **Dry run** | ✅ | `-n` / `--dry-run` |
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
| **JSON output format** | ✅ | `--format json` (walk, replace, undo, clean) |
| **Regex patterns** | ✅ | `--from 'figure ([0-9]+)' --to 'Figure \1'` |
| **Capturing groups** | ✅ | Back-reference `\1` tested |
| **Literal mode** | ✅ | `--literal --from 'foo.bar'` escapes regex |
| **Dotall mode** | ✅ | `--dotall` with `--at-once` |
| **At-once mode** | ✅ | `--at-once --dotall` for multiline patterns |
| **Parse-only** | ✅ | `-t --from 'foo' --to 'bar'` |
| **Stdin/stdout** | ✅ | `echo 'foo' \| run --from foo --to bar` |
| **Quiet mode** | ✅ | `-q` with diff to verify silent changes |
| **Moving files** | ❌ | (noted as TODO in golden-tests.sh) |
| **File collisions** | ✅ | Adds `.1` suffix when target exists |
| **Error cases** | ✅ | Invalid regex `'[invalid(regex'` |
| **Skill installation** | ✅ | `--install-skill --skill-scope=global` |
| **Skill instructions** | ✅ | `--skill` prints SKILL.md |

* * *

## New in v2-revs: Now Tested ✅

### 1. Claude Code Skill Installation (`repren/claude_skill.py`)

**Coverage: 45%** (82 statements, 37 covered)

This module provides `repren --install-skill` functionality.
Now has:

| Test Type | Coverage |
| --- | --- |
| Unit tests (`pytests.py`) | `get_skill_content()`, `install_skill()` global/project |
| Golden tests | `--skill`, `--install-skill --skill-scope=global` |
| CLI tests | `--install-skill` with scope validation |

### 2. JSON Output Format

**Coverage: Tested in golden tests** ✅

The v2-revs branch added comprehensive golden tests for JSON output:
- `--format json --walk-only`
- `--format json --dry-run --from X --to Y`
- `--format json --from X --to Y` (actual replace)
- `--format json --undo`
- `--format json --clean-backups`

* * *

## Proposed Golden Test Enhancements

### Phase 1: Add Missing CLI Flags

Add these sections to `golden-tests.sh`:

```bash
# --- Regex and capturing groups ---

cp -a original test-regex

# Create test file with figures
echo 'See figure 1 and figure 23 for details.' > test-regex/figures.txt

# Test capturing group replacement
run --from 'figure ([0-9]+)' --to 'Figure \1' test-regex/figures.txt
cat test-regex/figures.txt
# Expected: See Figure 1 and Figure 23 for details.


# --- Literal mode ---

cp -a original test-literal

# Create file with regex special chars
echo 'Match foo.bar and foo+bar here.' > test-literal/special.txt

# Without --literal: . matches any char (would match fooXbar too)
run --from 'foo.bar' --to 'REPLACED' test-literal/special.txt
cat test-literal/special.txt

# Reset and test with --literal
cp -a original test-literal2
echo 'Match foo.bar and fooXbar here.' > test-literal2/special.txt
run --literal --from 'foo.bar' --to 'REPLACED' test-literal2/special.txt
cat test-literal2/special.txt
# Expected: only foo.bar replaced, not fooXbar


# --- At-once mode (multiline patterns) ---

cp -a original test-atonce

# Create multiline test file
printf 'start\nmiddle\nend\n' > test-atonce/multiline.txt

# Default (line-by-line) won't match across lines
run -n --from 'start.*end' --to 'REPLACED' test-atonce/multiline.txt

# With --at-once and --dotall, pattern spans lines
run --at-once --dotall --from 'start.*end' --to 'REPLACED' test-atonce/multiline.txt
cat test-atonce/multiline.txt


# --- Parse-only mode ---

run -t --from 'foo' --to 'bar'
run -t -p patterns-misc


# --- Stdin/stdout mode ---

echo 'foo bar foo' | run --from foo --to bar
echo 'figure 1 and figure 2' | run --from 'figure ([0-9]+)' --to 'Fig. \1'


# --- Quiet mode ---

cp -a original test-quiet
run -q --from Humpty --to Dumpty test-quiet/humpty-dumpty.txt
# Should have no output but still make changes
diff original/humpty-dumpty.txt test-quiet/humpty-dumpty.txt || expect_error


# --- File collision handling ---

cp -a original test-collision
touch test-collision/dumpty-dumpty.txt  # Pre-existing target
run --renames --from humpty --to dumpty test-collision
ls_portable test-collision  # Should show collision handling


# --- Error cases ---

run --from '[invalid(regex' --to 'bar' original || expect_error
```

### Phase 2: Add Skill Installation Tests

```bash
# --- Skill installation ---

# Test global install (use temp HOME)
export ORIG_HOME="$HOME"
export HOME=$(mktemp -d)
run --install-skill --global --quiet
test -f "$HOME/.claude/skills/repren/SKILL.md" && echo "Global skill install: OK"
export HOME="$ORIG_HOME"

# Test project install
mkdir -p test-skill-project
cd test-skill-project
run --install-skill --project --quiet
test -f ".claude/skills/repren/SKILL.md" && echo "Project skill install: OK"
cd ..
```

* * *

## Unit Test Gaps (pytests.py)

The golden tests cover CLI behavior well, but some internal functions lack direct unit
tests:

### Functions Needing Unit Tests

| Function | Current Coverage | Priority |
| --- | --- | --- |
| `multi_replace()` | Indirect only | High |
| `_sort_drop_overlaps()` | Not tested | High |
| `transform_stream()` | Not tested | Medium |
| `transform_file()` | Not tested | Medium |
| `move_file()` | Not tested | Medium |
| `make_parent_dirs()` | Not tested | Low |
| `get_skill_content()` | Not tested | Medium |
| `install_skill()` | Not tested | Medium |

### Recommended Additions to pytests.py

```python
class TestMultiReplace:
    """Direct tests for multi_replace function."""

    def test_single_pattern(self):
        patterns = [(_compile("foo"), "bar")]
        result, count = multi_replace(patterns, "foo baz foo")
        assert result == "bar baz bar"
        assert count == 2

    def test_capturing_group(self):
        patterns = [(_compile(r"figure (\d+)"), r"Figure \1")]
        result, count = multi_replace(patterns, "See figure 1 and figure 23")
        assert result == "See Figure 1 and Figure 23"
        assert count == 2

    def test_overlapping_patterns(self):
        """When patterns overlap, first match wins."""
        patterns = [(_compile("foobar"), "LONG"), (_compile("foo"), "SHORT")]
        result, count = multi_replace(patterns, "foobar")
        assert result == "LONG"  # Not "SHORTbar"


class TestClaudeSkill:
    """Tests for Claude Code skill installation."""

    def test_get_skill_content_returns_markdown(self):
        from repren.claude_skill import get_skill_content
        content = get_skill_content()
        assert "repren" in content.lower()
        assert content.startswith("#") or "##" in content  # Markdown headers

    def test_install_skill_creates_file(self, tmp_path, monkeypatch):
        from repren.claude_skill import install_skill
        monkeypatch.setenv("HOME", str(tmp_path))
        install_skill(scope="global", interactive=False)
        skill_file = tmp_path / ".claude" / "skills" / "repren" / "SKILL.md"
        assert skill_file.exists()
```

* * *

## Coverage Summary

### Current State

| Component | Statements | Covered | Coverage |
| --- | --- | --- | --- |
| `repren/__init__.py` | 2 | 2 | 100% |
| `repren/repren.py` | 503 | 246 | 49% |
| `repren/claude_skill.py` | 82 | 37 | 45% |
| **Total** | **587** | **285** | **49%** |

### Coverage Trend

- **Before v2-revs:** 50% (458 statements)
- **After v2-revs:** 40% (586 statements)
- **After skill + CLI tests:** 46% (587 statements, 315 missed)
- **After unit tests for core functions:** 49% (587 statements, 302 missed)
- **Improvement:** +13 lines covered in `repren.py` for `multi_replace()` and
  `_sort_drop_overlaps()`

* * *

## Recommended Priority

### Completed (Now Tested) ✅

1. ~~**Regex capturing groups**~~ - Tested with `\1` back-reference
2. ~~**`--literal` mode**~~ - Tested
3. ~~**Stdin/stdout piping**~~ - Tested
4. ~~**Error cases**~~ - Invalid regex tested
5. ~~**`--at-once` + `--dotall`**~~ - Multiline patterns tested
6. ~~**`-t` / `--parse-only`**~~ - Tested
7. ~~**`-q` quiet mode**~~ - Tested
8. ~~**`--install-skill`**~~ - Golden + unit tests added
9. ~~**File collision handling**~~ - Tests rename with `.1` suffix
10. ~~**`claude_skill.py`**~~ - 45% coverage (was 0%)
11. ~~**`multi_replace()` direct tests**~~ - 9 unit tests added (single/multiple
    patterns, capturing groups, overlaps, unicode)
12. ~~**`_sort_drop_overlaps()`**~~ - 7 unit tests added (no overlaps, left/right/nested
    overlaps, sorting)
13. ~~**Moving files across directories**~~ - Golden test added for path-based renaming

### Remaining Gaps

All identified gaps have been addressed.
Future work could include:

#### Optional Enhancements

- **Additional edge cases** for multi-file moves with complex directory structures
- **Performance testing** with large codebases
- **CamelCase and whole word** pattern interactions

* * *

## Bug Fixes During Analysis

### Fixed: `--at-once` mode not applying changes

The `transform_stream()` function had a bug where `counts` was not updated with
`new_counts` in at-once mode, causing files to not be rewritten even when matches were
found. Fixed in `repren.py:761` by adding `counts.add(new_counts)`.

* * *

## Test Infrastructure Notes

1. **Golden tests renamed:** `tests.sh` → `golden-tests.sh`, `tests-expected.log` →
   `golden-tests-expected.log`

2. **Run tests with:**
   ```bash
   # All tests (unit + golden)
   make test
   
   # Just golden tests
   ./tests/run.sh
   
   # Update golden baseline after intentional changes
   make update-golden
   
   # Unit tests with coverage
   uv run pytest --cov=repren --cov-report=term-missing tests/pytests.py
   ```

3. **pytest-cov added** to dev dependencies for coverage reporting
