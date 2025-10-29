"""
Tests for globbing and gitignore support in repren.
"""
import os
import tempfile
from pathlib import Path
from typing import List

import pytest

from repren.repren import expand_globs, GitignoreFilter, is_glob_pattern


class TestGlobPatternDetection:
    """Test detection of glob patterns."""

    @pytest.mark.parametrize(
        "pattern, expected",
        [
            ("*.py", True),
            ("**/*.md", True),
            ("src/**/*.py", True),
            ("file.txt", False),
            ("/path/to/file.py", False),
            ("test_[abc].py", True),
            ("test_?.py", True),
            ("normal_path/file.txt", False),
        ],
    )
    def test_is_glob_pattern(self, pattern: str, expected: bool):
        """Test glob pattern detection."""
        assert is_glob_pattern(pattern) == expected


class TestGlobExpansion:
    """Test glob pattern expansion without gitignore."""

    def test_simple_glob_pattern(self, tmp_path: Path):
        """Test simple *.ext pattern."""
        # Create test files
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "file1.txt").touch()

        os.chdir(tmp_path)
        result = expand_globs(["*.py"], respect_gitignore=False)

        assert len(result) == 2
        assert str(tmp_path / "file1.py") in result
        assert str(tmp_path / "file2.py") in result

    def test_recursive_glob_pattern(self, tmp_path: Path):
        """Test **/*.ext recursive pattern."""
        # Create nested structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "file1.py").touch()
        (tmp_path / "src" / "nested").mkdir()
        (tmp_path / "src" / "nested" / "file2.py").touch()
        (tmp_path / "file3.py").touch()

        os.chdir(tmp_path)
        result = expand_globs(["**/*.py"], respect_gitignore=False)

        assert len(result) == 3
        assert str(tmp_path / "file3.py") in result
        assert str(tmp_path / "src" / "file1.py") in result
        assert str(tmp_path / "src" / "nested" / "file2.py") in result

    def test_multiple_patterns(self, tmp_path: Path):
        """Test multiple glob patterns."""
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.md").touch()
        (tmp_path / "file3.txt").touch()

        os.chdir(tmp_path)
        result = expand_globs(["*.py", "*.md"], respect_gitignore=False)

        assert len(result) == 2
        assert str(tmp_path / "file1.py") in result
        assert str(tmp_path / "file2.md") in result

    def test_mixed_globs_and_paths(self, tmp_path: Path):
        """Test mixing glob patterns with explicit paths."""
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "specific.txt").touch()

        os.chdir(tmp_path)
        result = expand_globs(
            ["*.py", str(tmp_path / "specific.txt")],
            respect_gitignore=False
        )

        assert len(result) == 3
        assert str(tmp_path / "file1.py") in result
        assert str(tmp_path / "file2.py") in result
        assert str(tmp_path / "specific.txt") in result

    def test_no_matches(self, tmp_path: Path):
        """Test glob pattern with no matches."""
        os.chdir(tmp_path)
        result = expand_globs(["*.nonexistent"], respect_gitignore=False)

        assert len(result) == 0

    def test_orig_files_always_excluded(self, tmp_path: Path):
        """Test that .orig files are always excluded from glob expansion."""
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.py.orig").touch()
        (tmp_path / "file3.txt.orig").touch()

        os.chdir(tmp_path)
        result = expand_globs(["*"], respect_gitignore=False)

        assert len(result) == 1
        assert str(tmp_path / "file1.py") in result
        # .orig files should not be included


class TestGitignoreFilter:
    """Test gitignore filtering functionality."""

    def test_basic_gitignore(self, tmp_path: Path):
        """Test basic gitignore pattern filtering."""
        # Create .gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n__pycache__/\n")

        # Create test files
        (tmp_path / "app.py").touch()
        (tmp_path / "error.log").touch()
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.pyc").touch()

        filter_obj = GitignoreFilter(str(tmp_path))

        assert not filter_obj.should_ignore(str(tmp_path / "app.py"))
        assert filter_obj.should_ignore(str(tmp_path / "error.log"))
        assert filter_obj.should_ignore(str(tmp_path / "__pycache__"))

    def test_nested_gitignore(self, tmp_path: Path):
        """Test nested .gitignore files."""
        # Root .gitignore
        (tmp_path / ".gitignore").write_text("*.log\n")

        # Nested .gitignore
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / ".gitignore").write_text("temp_*\n")

        # Create files
        (tmp_path / "root.log").touch()
        (tmp_path / "root.py").touch()
        (tmp_path / "subdir" / "sub.log").touch()
        (tmp_path / "subdir" / "temp_file.txt").touch()
        (tmp_path / "subdir" / "keep.txt").touch()

        filter_obj = GitignoreFilter(str(tmp_path / "subdir"))

        # Root .gitignore should apply
        assert filter_obj.should_ignore(str(tmp_path / "subdir" / "sub.log"))

        # Nested .gitignore should apply
        assert filter_obj.should_ignore(str(tmp_path / "subdir" / "temp_file.txt"))
        assert not filter_obj.should_ignore(str(tmp_path / "subdir" / "keep.txt"))

    def test_no_gitignore(self, tmp_path: Path):
        """Test behavior when no .gitignore exists."""
        (tmp_path / "file.py").touch()

        filter_obj = GitignoreFilter(str(tmp_path))

        assert not filter_obj.should_ignore(str(tmp_path / "file.py"))

    def test_dotfiles_and_dotdirs(self, tmp_path: Path):
        """Test handling of dotfiles (not ignored by default unless in .gitignore)."""
        (tmp_path / ".hidden").touch()
        (tmp_path / ".gitignore").write_text(".secret\n")
        (tmp_path / ".secret").touch()

        filter_obj = GitignoreFilter(str(tmp_path))

        # .hidden is not in gitignore, so not ignored
        assert not filter_obj.should_ignore(str(tmp_path / ".hidden"))

        # .secret is in gitignore
        assert filter_obj.should_ignore(str(tmp_path / ".secret"))

    def test_directory_patterns(self, tmp_path: Path):
        """Test directory-specific patterns."""
        (tmp_path / ".gitignore").write_text("build/\n")

        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "output.txt").touch()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").touch()

        filter_obj = GitignoreFilter(str(tmp_path))

        assert filter_obj.should_ignore(str(tmp_path / "build"))
        assert not filter_obj.should_ignore(str(tmp_path / "src"))


class TestGlobWithGitignore:
    """Test glob expansion with gitignore filtering."""

    def test_glob_respects_gitignore(self, tmp_path: Path):
        """Test that glob expansion respects .gitignore."""
        # Create .gitignore
        (tmp_path / ".gitignore").write_text("*.log\ntemp/\n")

        # Create files
        (tmp_path / "app.py").touch()
        (tmp_path / "error.log").touch()
        (tmp_path / "temp").mkdir()
        (tmp_path / "temp" / "cache.py").touch()

        os.chdir(tmp_path)
        result = expand_globs(["**/*"], respect_gitignore=True)

        # Should include app.py but not error.log or temp/cache.py
        assert str(tmp_path / "app.py") in result
        assert str(tmp_path / "error.log") not in result
        assert str(tmp_path / "temp" / "cache.py") not in result

    def test_glob_with_noignore_flag(self, tmp_path: Path):
        """Test that noignore flag disables gitignore filtering."""
        # Create .gitignore
        (tmp_path / ".gitignore").write_text("*.log\n")

        # Create files
        (tmp_path / "app.py").touch()
        (tmp_path / "error.log").touch()

        os.chdir(tmp_path)
        result = expand_globs(["**/*"], respect_gitignore=False)

        # Should include both files when gitignore is disabled
        assert str(tmp_path / "app.py") in result
        assert str(tmp_path / "error.log") in result

    def test_gitignore_file_itself_not_returned(self, tmp_path: Path):
        """Test that .gitignore files themselves are not returned in glob."""
        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "app.py").touch()

        os.chdir(tmp_path)
        result = expand_globs(["*"], respect_gitignore=True)

        # .gitignore should be excluded by default
        assert str(tmp_path / ".gitignore") not in result
        assert str(tmp_path / "app.py") in result
