# Test Coverage Analysis

## Current Test Architecture

The codebase uses **two complementary test approaches**:

### 1. Golden Tests (`tests/golden-tests.sh` → `tests/golden-tests-expected.log`)

Shell-based integration tests that capture CLI output and compare against expected results. This approach is excellent for:
- Testing actual user-facing behavior
- Catching regressions in output format
- Validating end-to-end workflows
- Documenting expected behavior through examples

### 2. Unit Tests (`tests/pytests.py`)

Python unit tests for internal functions. Current coverage: **40%** (586 statements, 351 missed)

---

## Golden Test Coverage Matrix

| Feature | Tested | Commands/Patterns Used |
|---------|--------|------------------------|
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
| **Regex patterns** | ❌ | Not tested |
| **Capturing groups** | ❌ | Not tested |
| **Literal mode** | ❌ | `--literal` |
| **Dotall mode** | ❌ | `--dotall` |
| **At-once mode** | ❌ | `--at-once` |
| **Parse-only** | ❌ | `-t` / `--parse-only` |
| **Stdin/stdout** | ❌ | Piped input |
| **Quiet mode** | ❌ | `-q` |
| **Moving files** | ❌ | (noted as TODO in golden-tests.sh) |
| **File collisions** | ❌ | Rename to existing name |
| **Error cases** | ❌ | Invalid patterns, permissions |

---

## New in v2-revs: Untested Components

### 1. Claude Code Skill Installation (`repren/claude_skill.py`)

**Coverage: 0%** (82 statements, all missed)

This new module provides `repren --install-skill` functionality. Functions needing tests:

| Function | Purpose | Test Approach |
|----------|---------|---------------|
| `get_skill_content()` | Load SKILL.md from package | Unit test |
| `install_skill()` | Install to ~/.claude or .claude | Integration test with temp dirs |
| `main()` | CLI argument parsing | Golden test or subprocess |

**Recommended golden test additions:**
```bash
# Test skill installation (use temp directory)
export HOME=$(mktemp -d)
run --install-skill --global --quiet
test -f "$HOME/.claude/skills/repren/SKILL.md" && echo "Global install OK"

# Test project-level install
mkdir -p test-skill-project && cd test-skill-project
run --install-skill --project --quiet
test -f ".claude/skills/repren/SKILL.md" && echo "Project install OK"
```

### 2. JSON Output Format

**Coverage: Tested in golden tests** ✅

The v2-revs branch added comprehensive golden tests for JSON output:
- `--format json --walk-only`
- `--format json --dry-run --from X --to Y`
- `--format json --from X --to Y` (actual replace)
- `--format json --undo`
- `--format json --clean-backups`

---

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

---

## Coverage Summary

### Current State (Post v2-revs Merge)

| Component | Statements | Covered | Coverage |
|-----------|------------|---------|----------|
| `repren/__init__.py` | 2 | 2 | 100% |
| `repren/repren.py` | 502 | 233 | 46% |
| `repren/claude_skill.py` | 82 | 0 | 0% |
| **Total** | **586** | **235** | **40%** |

### Coverage Trend

- **Before v2-revs:** 50% (458 statements)
- **After v2-revs:** 40% (586 statements)
- **Cause:** New `claude_skill.py` (82 lines, 0% covered) + expanded `repren.py`

---

## Recommended Priority

### High Priority (Extend Golden Tests)
1. **Regex capturing groups** - Core feature, untested
2. **`--literal` mode** - Important for non-regex users
3. **Stdin/stdout piping** - Common CLI usage pattern
4. **Error cases** - Invalid regex, missing files
5. **`--install-skill`** - New feature needs coverage

### Medium Priority (Golden Tests)
6. **`--at-once` + `--dotall`** - Multiline pattern support
7. **`-t` / `--parse-only`** - Debugging feature
8. **`-q` quiet mode** - Output control
9. **File collision handling** - Edge case

### Lower Priority (Unit Tests)
10. **`multi_replace()` direct tests** - Currently only indirect coverage
11. **`_sort_drop_overlaps()`** - Edge case handling
12. **`install_skill()` with temp dirs** - Installation paths

---

## Test Infrastructure Notes

1. **Golden tests renamed:** `tests.sh` → `golden-tests.sh`, `tests-expected.log` → `golden-tests-expected.log`

2. **Run tests with:**
   ```bash
   # Golden tests
   cd tests/work-dir && bash ../golden-tests.sh 2>&1 | diff - ../golden-tests-expected.log

   # Unit tests with coverage
   uv run pytest --cov=repren --cov-report=term-missing tests/pytests.py
   ```

3. **pytest-cov added** to dev dependencies for coverage reporting
