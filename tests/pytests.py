from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from repren.repren import (
    _split_name,
    to_lower_camel,
    to_lower_underscore,
    to_upper_camel,
    to_upper_underscore,
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
