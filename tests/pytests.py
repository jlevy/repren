from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from repren.repren import (
    _sort_drop_overlaps,
    _split_name,
    clean_backups,
    find_backup_files,
    multi_replace,
    parse_patterns,
    to_lower_camel,
    to_lower_underscore,
    to_upper_camel,
    to_upper_underscore,
    undo_backups,
    walk_files,
)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", ("", ["Ünicode", "String"])),
        ("sträßleTest", ("", ["sträßle", "Test"])),
        ("ГДеловойКод", ("", ["Г", "Деловой", "Код"])),
        ("ΚαλημέραWorld", ("", ["Καλημέρα", "World"])),
        ("normalTest", ("", ["normal", "Test"])),
        ("HTTPResponse", ("", ["HTTP", "Response"])),
        ("ThisIsATest", ("", ["This", "Is", "A", "Test"])),
        ("テストCase", ("", ["テスト", "Case"])),
        ("测试案例", ("", ["测试案例"])),  # Chinese characters
    ],
)
def test_split_name(input_str, expected):
    assert _split_name(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", "ünicodeString"),
        ("HTTPResponse", "httpResponse"),
        ("ΚαλημέραWorld", "καλημέραWorld"),
        ("sträßleTest", "sträßleTest"),
        ("ThisIsATest", "thisIsATest"),
        ("テストCase", "テストCase"),
        ("测试案例", "测试案例"),
    ],
)
def test_to_lower_camel(input_str, expected):
    assert to_lower_camel(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ünicode_string", "ÜnicodeString"),
        ("sträßle_test", "SträßleTest"),
        ("http_response", "HttpResponse"),
        ("καλημέρα_world", "ΚαλημέραWorld"),
        ("this_is_a_test", "ThisIsATest"),
        ("テスト_case", "テストCase"),
        ("测试_案例", "测试案例"),
    ],
)
def test_to_upper_camel(input_str, expected):
    assert to_upper_camel(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", "ünicode_string"),
        ("HTTPResponse", "http_response"),
        ("ΚαλημέραWorld", "καλημέρα_world"),
        ("sträßleTest", "sträßle_test"),
        ("ThisIsATest", "this_is_a_test"),
        ("テストCase", "テスト_case"),
        ("测试案例", "测试案例"),
    ],
)
def test_to_lower_underscore(input_str, expected):
    assert to_lower_underscore(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ünicode_string", "ÜNICODE_STRING"),
        ("http_response", "HTTP_RESPONSE"),
        ("καλημέρα_world", "ΚΑΛΗΜΈΡΑ_WORLD"),
        ("sträßle_test", "STRÄSSLE_TEST"),
        ("this_is_a_test", "THIS_IS_A_TEST"),
        ("テスト_case", "テスト_CASE"),
        ("测试_案例", "测试_案例"),
    ],
)
def test_to_upper_underscore(input_str, expected):
    assert to_upper_underscore(input_str) == expected


def test_integration_shell_tests():
    """
    Run the shell-based integration tests via run.sh.

    These tests exercise the full repren CLI with various argument combinations
    and compare output against a committed baseline for regression detection.
    """
    tests_dir = Path(__file__).parent
    run_script = tests_dir / "run.sh"

    result = subprocess.run(
        [str(run_script)],
        cwd=tests_dir.parent,  # Run from project root
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Include both stdout and stderr in failure message for debugging
        output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        pytest.fail(f"Integration tests failed (exit code {result.returncode}):\n{output}")


# --- Backup suffix tests ---


class TestWalkFilesBackupSuffix:
    """Tests for backup suffix filtering in walk_files."""

    def test_walk_files_skips_orig_files_in_directory(self):
        """Files ending in .orig should be excluded from directory walks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "file1.txt").write_text("content")
            Path(tmpdir, "file2.txt").write_text("content")
            Path(tmpdir, "file1.txt.orig").write_text("backup")

            files, skipped = walk_files([tmpdir])

            assert len(files) == 2
            assert any("file1.txt" in f and not f.endswith(".orig") for f in files)
            assert any("file2.txt" in f for f in files)
            assert not any(f.endswith(".orig") for f in files)
            assert skipped == 1

    def test_walk_files_skips_custom_backup_suffix(self):
        """Files ending in custom backup suffix should be excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt").write_text("content")
            Path(tmpdir, "file1.txt.bak").write_text("backup")

            files, skipped = walk_files([tmpdir], backup_suffix=".bak")

            assert len(files) == 1
            assert not any(f.endswith(".bak") for f in files)
            assert skipped == 1

    def test_walk_files_skips_explicit_backup_files(self):
        """Explicit file paths ending in backup suffix should also be filtered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            normal_file = Path(tmpdir, "file.txt")
            backup_file = Path(tmpdir, "file.txt.orig")
            normal_file.write_text("content")
            backup_file.write_text("backup")

            files, skipped = walk_files([str(normal_file), str(backup_file)])

            assert len(files) == 1
            assert files[0] == str(normal_file)
            assert skipped == 1

    def test_walk_files_no_skipped_files_returns_zero(self):
        """When no backup files exist, skipped count should be 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt").write_text("content")
            Path(tmpdir, "file2.txt").write_text("content")

            files, skipped = walk_files([tmpdir])

            assert len(files) == 2
            assert skipped == 0


class TestBackupSuffixValidation:
    """Tests for --backup-suffix CLI validation."""

    def test_backup_suffix_must_start_with_dot(self):
        """Backup suffix validation error when suffix doesn't start with '.'."""
        result = subprocess.run(
            ["uv", "run", "repren", "--backup-suffix", "bak", "--from", "a", "--to", "b", "."],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert (
            "must start with '.'" in result.stderr.lower()
            or "must start with '.'" in result.stdout.lower()
        )

    def test_backup_suffix_valid_with_dot(self):
        """Backup suffix should be accepted when it starts with '.'."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "repren",
                "--backup-suffix",
                ".bak",
                "--dry-run",
                "--from",
                "a",
                "--to",
                "b",
            ],
            capture_output=True,
            text=True,
            input="test",
        )
        # Should not fail on suffix validation (may fail for other reasons like missing paths)
        assert "must start with '.'" not in result.stderr.lower()


# --- Undo mode tests ---


class TestFindBackupFiles:
    """Tests for find_backup_files function."""

    def test_find_backup_files_in_directory(self):
        """Should find all .orig files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt").write_text("content")
            Path(tmpdir, "file1.txt.orig").write_text("backup")
            Path(tmpdir, "file2.txt.orig").write_text("backup2")

            backups = find_backup_files([tmpdir])

            assert len(backups) == 2
            assert any("file1.txt.orig" in f for f in backups)
            assert any("file2.txt.orig" in f for f in backups)

    def test_find_backup_files_custom_suffix(self):
        """Should find files with custom backup suffix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt.bak").write_text("backup")
            Path(tmpdir, "file1.txt.orig").write_text("other backup")

            backups = find_backup_files([tmpdir], backup_suffix=".bak")

            assert len(backups) == 1
            assert backups[0].endswith(".bak")

    def test_find_backup_files_respects_include_exclude(self):
        """Should respect include and exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt.orig").write_text("backup")
            Path(tmpdir, "file2.py.orig").write_text("backup")

            backups = find_backup_files([tmpdir], include_pat=r".*\.txt\.orig$")

            assert len(backups) == 1
            assert "file1.txt.orig" in backups[0]


class TestUndoBackups:
    """Tests for undo_backups function."""

    def test_undo_content_only_change(self):
        """Undo a file where only content was changed (no rename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate: file.txt was modified, .orig backup exists
            current_file = Path(tmpdir, "file.txt")
            backup_file = Path(tmpdir, "file.txt.orig")

            backup_file.write_text("original content")
            current_file.write_text("modified content")

            # Make sure backup is older
            import time

            time.sleep(0.01)
            current_file.write_text("modified content")

            patterns = parse_patterns("foo\tbar")  # Pattern that doesn't affect filename

            restored, skipped = undo_backups([tmpdir], patterns)

            assert restored == 1
            assert skipped == 0
            assert current_file.read_text() == "original content"
            assert not backup_file.exists()

    def test_undo_file_rename(self):
        """Undo a file that was renamed."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate: OldClass.txt was renamed to NewClass.txt
            # Use unique names that won't match temp directory paths
            backup_file = Path(tmpdir, "OldClass.txt.orig")
            renamed_file = Path(tmpdir, "NewClass.txt")

            # Create backup first (older)
            backup_file.write_text("original content")
            time.sleep(0.01)
            # Create renamed file after (newer)
            renamed_file.write_text("content")

            patterns = parse_patterns("OldClass\tNewClass")

            restored, skipped = undo_backups([tmpdir], patterns)

            assert restored == 1
            assert skipped == 0
            original_file = Path(tmpdir, "OldClass.txt")
            assert original_file.read_text() == "original content"
            assert not backup_file.exists()
            assert not renamed_file.exists()

    def test_undo_skips_when_predicted_file_not_found(self):
        """Skip undo when the predicted renamed file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_file = Path(tmpdir, "OldClass.txt.orig")
            backup_file.write_text("original")
            # The renamed file (NewClass.txt) doesn't exist

            patterns = parse_patterns("OldClass\tNewClass")

            restored, skipped = undo_backups([tmpdir], patterns)

            assert restored == 0
            assert skipped == 1
            assert backup_file.exists()  # Backup should still exist

    def test_undo_skips_when_backup_is_newer(self):
        """Skip undo when backup is newer than current file (unexpected)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            current_file = Path(tmpdir, "file.txt")
            backup_file = Path(tmpdir, "file.txt.orig")

            current_file.write_text("modified content")
            import time

            time.sleep(0.01)
            backup_file.write_text("original content")  # Backup is newer (unusual)

            patterns = parse_patterns("foo\tbar")

            restored, skipped = undo_backups([tmpdir], patterns)

            assert restored == 0
            assert skipped == 1
            assert current_file.read_text() == "modified content"
            assert backup_file.exists()

    def test_undo_dry_run(self):
        """Dry run should not modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            current_file = Path(tmpdir, "file.txt")
            backup_file = Path(tmpdir, "file.txt.orig")

            backup_file.write_text("original")
            current_file.write_text("modified")

            patterns = parse_patterns("foo\tbar")

            restored, skipped = undo_backups([tmpdir], patterns, dry_run=True)

            assert restored == 1  # Would have restored
            assert skipped == 0
            assert current_file.read_text() == "modified"  # Still has modified content
            assert backup_file.exists()  # Backup still exists


class TestUndoCLI:
    """Tests for --undo CLI argument."""

    def test_undo_requires_patterns(self):
        """--undo should require pattern specification."""
        result = subprocess.run(
            ["uv", "run", "repren", "--undo", "."],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        # Should complain about missing patterns
        assert "patterns" in result.stderr.lower() or "from" in result.stderr.lower()


# --- Clean backups tests ---


class TestCleanBackups:
    """Tests for clean_backups function."""

    def test_clean_backups_removes_orig_files(self):
        """Should remove all .orig backup files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            normal_file = Path(tmpdir, "file.txt")
            backup_file1 = Path(tmpdir, "file.txt.orig")
            backup_file2 = Path(tmpdir, "other.txt.orig")

            normal_file.write_text("content")
            backup_file1.write_text("backup1")
            backup_file2.write_text("backup2")

            removed = clean_backups([tmpdir])

            assert removed == 2
            assert normal_file.exists()
            assert not backup_file1.exists()
            assert not backup_file2.exists()

    def test_clean_backups_custom_suffix(self):
        """Should remove files with custom backup suffix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_bak = Path(tmpdir, "file.txt.bak")
            backup_orig = Path(tmpdir, "file.txt.orig")

            backup_bak.write_text("backup bak")
            backup_orig.write_text("backup orig")

            removed = clean_backups([tmpdir], backup_suffix=".bak")

            assert removed == 1
            assert not backup_bak.exists()
            assert backup_orig.exists()  # Should not be removed

    def test_clean_backups_dry_run(self):
        """Dry run should not remove files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_file = Path(tmpdir, "file.txt.orig")
            backup_file.write_text("backup")

            removed = clean_backups([tmpdir], dry_run=True)

            assert removed == 1  # Would have removed
            assert backup_file.exists()  # But file still exists

    def test_clean_backups_respects_include_exclude(self):
        """Should respect include and exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup1 = Path(tmpdir, "file1.txt.orig")
            backup2 = Path(tmpdir, "file2.py.orig")

            backup1.write_text("backup1")
            backup2.write_text("backup2")

            removed = clean_backups([tmpdir], include_pat=r".*\.txt\.orig$")

            assert removed == 1
            assert not backup1.exists()
            assert backup2.exists()


class TestCleanBackupsCLI:
    """Tests for --clean-backups CLI argument."""

    def test_clean_backups_standalone(self):
        """--clean-backups should work without patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_file = Path(tmpdir, "file.txt.orig")
            backup_file.write_text("backup")

            result = subprocess.run(
                ["uv", "run", "repren", "--clean-backups", tmpdir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert not backup_file.exists()

    def test_clean_backups_conflicts_with_patterns(self):
        """--clean-backups should conflict with --from/--to."""
        result = subprocess.run(
            ["uv", "run", "repren", "--clean-backups", "--from", "a", "--to", "b", "."],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


# --- Claude Skill tests ---


class TestClaudeSkillContent:
    """Tests for Claude skill content loading."""

    def test_get_skill_content_returns_markdown(self):
        """get_skill_content should return valid markdown content."""
        from repren.claude_skill import get_skill_content

        content = get_skill_content()

        assert isinstance(content, str)
        assert len(content) > 100  # Should have substantial content
        assert "repren" in content.lower()
        # Should be valid markdown with headers
        assert "#" in content

    def test_skill_content_has_required_sections(self):
        """Skill content should have essential sections for Claude."""
        from repren.claude_skill import get_skill_content

        content = get_skill_content()

        # Should have usage examples
        assert "example" in content.lower() or "--from" in content
        # Should mention key features
        assert "pattern" in content.lower() or "replace" in content.lower()


class TestClaudeSkillInstallation:
    """Tests for Claude skill installation."""

    def test_install_skill_global_creates_file(self):
        """install_skill with global scope should create file in ~/.claude/skills."""
        from repren.claude_skill import install_skill

        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock HOME to use temp directory
            import os

            old_home = os.environ.get("HOME")
            os.environ["HOME"] = tmpdir

            try:
                install_skill()  # Default is global (uses HOME)

                skill_file = Path(tmpdir) / ".claude" / "skills" / "repren" / "SKILL.md"
                assert skill_file.exists()
                content = skill_file.read_text()
                assert "repren" in content.lower()
            finally:
                if old_home:
                    os.environ["HOME"] = old_home

    def test_install_skill_project_creates_file(self):
        """install_skill with agent_base should create file in specified location."""
        from repren.claude_skill import install_skill

        with tempfile.TemporaryDirectory() as tmpdir:
            # agent_base IS the .claude directory itself
            agent_base = Path(tmpdir) / ".claude"
            install_skill(agent_base=str(agent_base))

            skill_file = agent_base / "skills" / "repren" / "SKILL.md"
            assert skill_file.exists()
            content = skill_file.read_text()
            assert "repren" in content.lower()

    def test_install_skill_content_matches_package(self):
        """Installed skill content should match package content."""
        from repren.claude_skill import get_skill_content, install_skill

        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            old_home = os.environ.get("HOME")
            os.environ["HOME"] = tmpdir

            try:
                install_skill()  # Default is global (uses HOME)

                skill_file = Path(tmpdir) / ".claude" / "skills" / "repren" / "SKILL.md"
                installed_content = skill_file.read_text()
                package_content = get_skill_content()

                assert installed_content == package_content
            finally:
                if old_home:
                    os.environ["HOME"] = old_home


class TestClaudeSkillCLI:
    """Tests for Claude skill CLI options."""

    def test_skill_instructions_prints_content(self):
        """--skill should print skill content."""
        result = subprocess.run(
            ["uv", "run", "repren", "--skill"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "repren" in result.stdout.lower()
        # Should have markdown content
        assert "#" in result.stdout

    def test_install_skill_with_agent_base(self):
        """--install-skill with --agent-base should work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # agent_base IS the .claude directory itself
            agent_base = Path(tmpdir) / ".claude"
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "repren",
                    "--install-skill",
                    f"--agent-base={agent_base}",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            skill_file = agent_base / "skills" / "repren" / "SKILL.md"
            assert skill_file.exists()


# --- multi_replace tests ---


class TestMultiReplace:
    """Direct tests for the multi_replace function."""

    def test_single_pattern(self):
        """Single pattern replacement."""
        patterns = parse_patterns("foo\tbar")
        result, counts = multi_replace(b"foo baz foo", patterns)

        assert result == b"bar baz bar"
        assert counts.found == 2
        assert counts.valid == 2

    def test_no_matches(self):
        """No matches should return input unchanged."""
        patterns = parse_patterns("xyz\tabc")
        result, counts = multi_replace(b"foo baz foo", patterns)

        assert result == b"foo baz foo"
        assert counts.found == 0
        assert counts.valid == 0

    def test_multiple_patterns(self):
        """Multiple non-overlapping patterns."""
        patterns = parse_patterns("foo\tFOO\nbar\tBAR")
        result, counts = multi_replace(b"foo bar baz", patterns)

        assert result == b"FOO BAR baz"
        assert counts.found == 2
        assert counts.valid == 2

    def test_capturing_group(self):
        """Pattern with capturing group and back-reference."""
        # parse_patterns expects actual tab separator
        patterns = parse_patterns("figure ([0-9]+)\tFigure \\1")
        result, counts = multi_replace(b"See figure 1 and figure 23", patterns)

        assert result == b"See Figure 1 and Figure 23"
        assert counts.found == 2
        assert counts.valid == 2

    def test_overlapping_patterns_first_wins(self):
        """When patterns overlap, first match (by position) wins."""
        # Create patterns where "foobar" and "foo" could both match
        patterns = parse_patterns("foobar\tLONG\nfoo\tSHORT")
        result, counts = multi_replace(b"foobar", patterns)

        # "foobar" matches first, so "foo" is dropped as overlapping
        assert result == b"LONG"
        assert counts.found == 2  # Both patterns matched
        assert counts.valid == 1  # But only one was applied (no overlap)

    def test_nested_overlap(self):
        """Inner match nested within outer match should be dropped."""
        # "abcd" contains "bc" - both match but overlap
        patterns = parse_patterns("abcd\tOUTER\nbc\tINNER")
        result, counts = multi_replace(b"abcd", patterns)

        assert result == b"OUTER"
        assert counts.found == 2
        assert counts.valid == 1

    def test_adjacent_non_overlapping(self):
        """Adjacent but non-overlapping matches should both apply."""
        patterns = parse_patterns("foo\tFOO\nbar\tBAR")
        result, counts = multi_replace(b"foobar", patterns)

        assert result == b"FOOBAR"
        assert counts.found == 2
        assert counts.valid == 2

    def test_empty_input(self):
        """Empty input should return empty output."""
        patterns = parse_patterns("foo\tbar")
        result, counts = multi_replace(b"", patterns)

        assert result == b""
        assert counts.found == 0
        assert counts.valid == 0

    def test_unicode_content(self):
        """Unicode content should be handled correctly."""
        patterns = parse_patterns("café\tcoffee")
        result, counts = multi_replace("Un café s'il vous plaît".encode(), patterns)

        assert result == "Un coffee s'il vous plaît".encode()
        assert counts.found == 1
        assert counts.valid == 1


# --- _sort_drop_overlaps tests ---


class TestSortDropOverlaps:
    """Direct tests for _sort_drop_overlaps function."""

    def _make_match(self, pattern: str, text: str, pos: int = 0):
        """Helper to create a match object at a specific position."""
        import re

        regex = re.compile(pattern.encode("utf-8"))
        for m in regex.finditer(text.encode("utf-8")):
            if m.start() >= pos:
                return m
        return None

    def test_no_overlaps(self):
        """Non-overlapping matches should all be kept."""
        import re

        text = b"foo bar baz"
        matches = []
        for pattern, replacement in [(b"foo", b"FOO"), (b"bar", b"BAR"), (b"baz", b"BAZ")]:
            regex = re.compile(pattern)
            for m in regex.finditer(text):
                matches.append((m, replacement))

        result = _sort_drop_overlaps(matches)

        assert len(result) == 3
        # Results should be sorted by position
        assert result[0][1] == b"FOO"
        assert result[1][1] == b"BAR"
        assert result[2][1] == b"BAZ"

    def test_overlapping_left(self):
        """Match overlapping with previous match should be dropped."""
        import re

        text = b"foobar"
        matches = []
        # "foo" at position 0-3
        regex1 = re.compile(b"foo")
        for m in regex1.finditer(text):
            matches.append((m, b"ONE"))
        # "oob" at position 1-4 overlaps with "foo"
        regex2 = re.compile(b"oob")
        for m in regex2.finditer(text):
            matches.append((m, b"TWO"))

        result = _sort_drop_overlaps(matches)

        assert len(result) == 1
        assert result[0][1] == b"ONE"  # First by position wins

    def test_overlapping_right(self):
        """Match overlapping with next match should be dropped."""
        import re

        text = b"foobar"
        matches = []
        # "oob" at position 1-4
        regex1 = re.compile(b"oob")
        for m in regex1.finditer(text):
            matches.append((m, b"ONE"))
        # "bar" at position 3-6 overlaps with "oob"
        regex2 = re.compile(b"bar")
        for m in regex2.finditer(text):
            matches.append((m, b"TWO"))

        result = _sort_drop_overlaps(matches)

        assert len(result) == 1
        # "oob" starts at 1, "bar" starts at 3, so "oob" is inserted first
        # "bar" overlaps with "oob" on its left and gets dropped
        assert result[0][1] == b"ONE"

    def test_nested_match(self):
        """Match completely nested inside another should be dropped."""
        import re

        text = b"abcdef"
        matches = []
        # "bcde" at position 1-5
        regex1 = re.compile(b"bcde")
        for m in regex1.finditer(text):
            matches.append((m, b"OUTER"))
        # "cd" at position 2-4 is inside "bcde"
        regex2 = re.compile(b"cd")
        for m in regex2.finditer(text):
            matches.append((m, b"INNER"))

        result = _sort_drop_overlaps(matches)

        assert len(result) == 1
        assert result[0][1] == b"OUTER"

    def test_empty_input(self):
        """Empty match list should return empty list."""
        result = _sort_drop_overlaps([])
        assert result == []

    def test_single_match(self):
        """Single match should be returned as-is."""
        import re

        text = b"foo"
        regex = re.compile(b"foo")
        matches = [(m, b"bar") for m in regex.finditer(text)]

        result = _sort_drop_overlaps(matches)

        assert len(result) == 1
        assert result[0][1] == b"bar"

    def test_maintains_sorted_order(self):
        """Output should always be sorted by match position."""
        import re

        text = b"aaa bbb ccc"
        matches = []
        # Add matches in reverse order
        for pattern, replacement in [(b"ccc", b"C"), (b"bbb", b"B"), (b"aaa", b"A")]:
            regex = re.compile(pattern)
            for m in regex.finditer(text):
                matches.append((m, replacement))

        result = _sort_drop_overlaps(matches)

        assert len(result) == 3
        # Should be sorted by position regardless of input order
        assert result[0][0].start() < result[1][0].start() < result[2][0].start()
        assert result[0][1] == b"A"
        assert result[1][1] == b"B"
        assert result[2][1] == b"C"
