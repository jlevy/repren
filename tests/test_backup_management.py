"""
Tests for backup file management features in repren.
"""
import os
from pathlib import Path
from typing import List

import pytest

from repren.repren import (
    remove_backups,
    transform_file,
    rewrite_files,
    parse_patterns,
    BACKUP_SUFFIX,
)


class TestNoBackupOption:
    """Test the --nobackup option."""

    def test_transform_file_with_backup(self, tmp_path: Path):
        """Test that backups are created by default."""
        source = tmp_path / "test.txt"
        source.write_bytes(b"hello world")

        patterns = parse_patterns("world\tuniverse")

        def transform(contents: bytes):
            from repren.repren import multi_replace
            return multi_replace(contents, patterns)

        from repren.repren import transform_file

        transform_file(
            transform,
            str(source),
            str(source),
            create_backup=True,
            dry_run=False,
        )

        # Backup should exist
        backup = tmp_path / f"test.txt{BACKUP_SUFFIX}"
        assert backup.exists()
        assert backup.read_bytes() == b"hello world"

        # Original should be modified
        assert source.read_bytes() == b"hello universe"

    def test_transform_file_without_backup(self, tmp_path: Path):
        """Test that backups are not created when create_backup=False."""
        source = tmp_path / "test.txt"
        source.write_bytes(b"hello world")

        patterns = parse_patterns("world\tuniverse")

        def transform(contents: bytes):
            from repren.repren import multi_replace
            return multi_replace(contents, patterns)

        from repren.repren import transform_file

        transform_file(
            transform,
            str(source),
            str(source),
            create_backup=False,
            dry_run=False,
        )

        # Backup should NOT exist
        backup = tmp_path / f"test.txt{BACKUP_SUFFIX}"
        assert not backup.exists()

        # Original should still be modified
        assert source.read_bytes() == b"hello universe"

    def test_nobackup_with_rename(self, tmp_path: Path):
        """Test nobackup option when file is renamed."""
        source = tmp_path / "old_name.txt"
        dest = tmp_path / "new_name.txt"
        source.write_text("content")

        def transform(contents: bytes):
            from repren.repren import _MatchCounts
            return contents, _MatchCounts()

        from repren.repren import transform_file

        transform_file(
            transform,
            str(source),
            str(dest),
            create_backup=False,
            dry_run=False,
        )

        # Old file should not exist
        assert not source.exists()
        # New file should exist
        assert dest.exists()
        # No backup should exist
        assert not (tmp_path / f"old_name.txt{BACKUP_SUFFIX}").exists()

    def test_nobackup_dry_run(self, tmp_path: Path):
        """Test that dry-run with nobackup doesn't create files."""
        source = tmp_path / "test.txt"
        source.write_text("hello world")

        patterns = parse_patterns("world\tuniverse")

        def transform(contents: bytes):
            from repren.repren import multi_replace
            return multi_replace(contents, patterns)

        from repren.repren import transform_file

        transform_file(
            transform,
            str(source),
            str(source),
            create_backup=False,
            dry_run=True,
        )

        # Original should be unchanged
        assert source.read_text() == "hello world"
        # No backup should exist
        assert not (tmp_path / f"test.txt{BACKUP_SUFFIX}").exists()


class TestRemoveBackups:
    """Test the remove_backups function."""

    def test_remove_backups_basic(self, tmp_path: Path):
        """Test basic backup removal."""
        # Create some files and backups
        (tmp_path / "file1.txt").touch()
        (tmp_path / f"file1.txt{BACKUP_SUFFIX}").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / f"file2.py{BACKUP_SUFFIX}").touch()
        (tmp_path / "keep.txt").touch()

        count = remove_backups(str(tmp_path), dry_run=False)

        assert count == 2
        assert not (tmp_path / f"file1.txt{BACKUP_SUFFIX}").exists()
        assert not (tmp_path / f"file2.py{BACKUP_SUFFIX}").exists()
        assert (tmp_path / "file1.txt").exists()
        assert (tmp_path / "file2.py").exists()
        assert (tmp_path / "keep.txt").exists()

    def test_remove_backups_recursive(self, tmp_path: Path):
        """Test recursive backup removal."""
        # Create nested structure with backups
        (tmp_path / "root.txt").touch()
        (tmp_path / f"root.txt{BACKUP_SUFFIX}").touch()

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").touch()
        (subdir / f"nested.txt{BACKUP_SUFFIX}").touch()

        deepdir = subdir / "deep"
        deepdir.mkdir()
        (deepdir / "deep.txt").touch()
        (deepdir / f"deep.txt{BACKUP_SUFFIX}").touch()

        count = remove_backups(str(tmp_path), dry_run=False)

        assert count == 3
        assert not (tmp_path / f"root.txt{BACKUP_SUFFIX}").exists()
        assert not (subdir / f"nested.txt{BACKUP_SUFFIX}").exists()
        assert not (deepdir / f"deep.txt{BACKUP_SUFFIX}").exists()

    def test_remove_backups_dry_run(self, tmp_path: Path):
        """Test dry-run mode for backup removal."""
        (tmp_path / f"file1.txt{BACKUP_SUFFIX}").touch()
        (tmp_path / f"file2.py{BACKUP_SUFFIX}").touch()

        count = remove_backups(str(tmp_path), dry_run=True)

        # Should report count but not remove
        assert count == 2
        assert (tmp_path / f"file1.txt{BACKUP_SUFFIX}").exists()
        assert (tmp_path / f"file2.py{BACKUP_SUFFIX}").exists()

    def test_remove_backups_no_backups(self, tmp_path: Path):
        """Test backup removal when no backups exist."""
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()

        count = remove_backups(str(tmp_path), dry_run=False)

        assert count == 0

    def test_remove_backups_only_backups(self, tmp_path: Path):
        """Test removing backups when original files don't exist."""
        # Create only backup files (orphaned backups)
        (tmp_path / f"deleted1.txt{BACKUP_SUFFIX}").touch()
        (tmp_path / f"deleted2.py{BACKUP_SUFFIX}").touch()

        count = remove_backups(str(tmp_path), dry_run=False)

        assert count == 2
        assert not (tmp_path / f"deleted1.txt{BACKUP_SUFFIX}").exists()
        assert not (tmp_path / f"deleted2.py{BACKUP_SUFFIX}").exists()

    def test_remove_backups_with_logging(self, tmp_path: Path):
        """Test that backup removal logs correctly."""
        (tmp_path / f"file1.txt{BACKUP_SUFFIX}").touch()

        logged_messages: List[str] = []

        def log_func(msg: str):
            logged_messages.append(msg)

        count = remove_backups(str(tmp_path), dry_run=False, log=log_func)

        assert count == 1
        assert len(logged_messages) > 0
        # Check that file was mentioned in logs
        assert any("file1.txt" in msg for msg in logged_messages)

    def test_remove_backups_empty_directory(self, tmp_path: Path):
        """Test backup removal in empty directory."""
        count = remove_backups(str(tmp_path), dry_run=False)
        assert count == 0


class TestBackupIntegration:
    """Integration tests for backup features with full repren workflow."""

    def test_full_workflow_with_nobackup(self, tmp_path: Path):
        """Test complete workflow with --nobackup flag."""
        # Create test files
        (tmp_path / "file1.txt").write_bytes(b"foo bar")
        (tmp_path / "file2.txt").write_bytes(b"foo baz")

        patterns = parse_patterns("foo\tqux")

        # This will be tested via command-line integration
        # For now, we test the underlying functions
        from repren.repren import rewrite_file

        rewrite_file(
            str(tmp_path / "file1.txt"),
            patterns,
            do_contents=True,
            create_backup=False,
            dry_run=False,
        )

        assert (tmp_path / "file1.txt").read_bytes() == b"qux bar"
        assert not (tmp_path / f"file1.txt{BACKUP_SUFFIX}").exists()

    def test_combine_remove_backups_and_rewrite(self, tmp_path: Path):
        """Test removing old backups before doing new operations."""
        # Create old backups
        (tmp_path / f"old1.txt{BACKUP_SUFFIX}").touch()
        (tmp_path / f"old2.txt{BACKUP_SUFFIX}").touch()

        # Remove old backups
        remove_count = remove_backups(str(tmp_path), dry_run=False)
        assert remove_count == 2

        # Now do new operations
        (tmp_path / "new.txt").write_bytes(b"test")
        patterns = parse_patterns("test\tresult")

        from repren.repren import rewrite_file

        rewrite_file(
            str(tmp_path / "new.txt"),
            patterns,
            do_contents=True,
            create_backup=True,
            dry_run=False,
        )

        # Old backups should be gone
        assert not (tmp_path / f"old1.txt{BACKUP_SUFFIX}").exists()
        assert not (tmp_path / f"old2.txt{BACKUP_SUFFIX}").exists()

        # New backup should exist
        assert (tmp_path / f"new.txt{BACKUP_SUFFIX}").exists()
        assert (tmp_path / f"new.txt{BACKUP_SUFFIX}").read_bytes() == b"test"
        assert (tmp_path / "new.txt").read_bytes() == b"result"
