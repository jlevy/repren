#!/bin/bash

# Test script. Output of this script can be saved and compared to test for regressions.
# Double-spacing between commands here makes the script output easier to read.

# We turn on exit on error, so that any status code changes cause a test failure.
set -e -o pipefail

prog_name=repren

args=
#args=--debug

run() {
  uv run repren $args "$@"
}

# A trick to test for error conditions.
expect_error() {
  echo "(got expected error: status $?)"
}

# A trick to do ls portably, showing just files, types, and permissions.
# Macos appends an @ to permissions, so we strip it.
ls_portable() {
  ls -lF "$@" | tail -n +2 | awk '{gsub(/@/, "", $1); print $1, $NF}'
}

# This will echo all commands as they are read. Bash commands plus their
# outputs will be used for validating regression tests pass (set -x is similar
# but less readable and sometimes not deterministic).
set -v

# --- Start of tests ---

run || expect_error

# Text replacements, no renames.

cp -a original test1

run -n --from Humpty --to Dumpty test1/humpty-dumpty.txt

diff -r original test1

run --from humpty --to dumpty test1/humpty-dumpty.txt

diff original test1

run --from Humpty --to Dumpty test1/humpty-dumpty.txt

diff -r original test1 || expect_error

run --from humpty --to dumpty test1


# File renames only.

cp -a original test2

run -n --renames --from humpty --to dumpty test2

ls_portable test2

run --renames --from humpty --to dumpty test2

ls_portable test2

diff -r original test2 || expect_error


# Both file renames and replacements.

cp -a original test3

run -n --full -i --from humpty --to dumpty test3

ls_portable test3

run --full -i --from humpty --to dumpty test3

ls_portable test3

diff -r original test3 || expect_error


# More patterns: Contents.

cp -a original test4

run -p patterns-misc test4

diff -r original test4 || expect_error


# More patterns: Contents and renames.

cp -a original test5

run --full -i -p patterns-misc test5

diff -r original test5 || expect_error


# Preserving case.

cp -a original test6

run --full --preserve-case -p patterns-rotate-abc test6/humpty-dumpty.txt

diff -r original test6 || expect_error


# A few rotations to get back to where we started.

cp -a original test7

run --full --preserve-case -p patterns-rotate-abc test7

run --full --preserve-case -p patterns-rotate-abc test7

run --full --preserve-case -p patterns-rotate-abc test7

find test7 -name \*.orig -delete

diff -r original test7


# Whole-word mode.

cp -a original test8

run --full --word-breaks -p patterns-rotate-abc test8

diff -r original/humpty-dumpty.txt test8/humpty-dumpty.txt || expect_error


# Include/exclude patterns.

run --walk-only original

run --walk-only --include='.*[.]txt$' original

run --walk-only --exclude='beech|maple' original

run --walk-only --include='A.*|M.*|oak' --exclude='Mex.*' original


# Moving files across directories.

cp -a original test-move

# First, let's see what files exist
ls_portable test-move/stuff/trees

# Create target directory structure (repren expects parent dirs to exist for moves)
mkdir -p test-move/relocated

# Rename files from stuff/trees to relocated directory
# This tests path-based renaming that effectively moves files
run --renames --from 'stuff/trees' --to 'relocated' test-move

# Show result - files should have moved
ls_portable test-move/stuff/trees 2>/dev/null || echo "(directory removed or empty)"
ls_portable test-move/relocated


# Backup management: undo and clean-backups.

cp -a original test-backup

# Make a change with renames (creates backup files).
run --full -i --from humpty --to dumpty test-backup

ls_portable test-backup

# Verify backup exists and content changed.
cat test-backup/humpty-dumpty.txt.orig | head -1

cat test-backup/dumpty-dumpty.txt | head -1

# Dry run undo to preview what would be restored.
run --undo -n --full -i --from humpty --to dumpty test-backup

# Actually undo the changes.
run --undo --full -i --from humpty --to dumpty test-backup

ls_portable test-backup

# Verify content is restored.
cat test-backup/humpty-dumpty.txt | head -1

# Verify we're back to original state.
diff -r original test-backup

# Redo the change for clean-backups test.
run --full -i --from humpty --to dumpty test-backup

ls_portable test-backup

# Dry run clean-backups to preview what would be removed.
run --clean-backups -n test-backup

# Actually clean the backups.
run --clean-backups test-backup

ls_portable test-backup

# Verify changes remain but backups are gone.
diff -r original test-backup || expect_error


# Custom backup suffix.

cp -a original test-suffix

# Use custom backup suffix.
run --full -i --from humpty --to dumpty --backup-suffix .bak test-suffix

ls_portable test-suffix

# Clean backups with custom suffix.
run --clean-backups --backup-suffix .bak test-suffix

ls_portable test-suffix


# JSON output format tests.

cp -a original test-json

# JSON output for walk-only.
run --format json --walk-only test-json

# JSON output for dry-run replacement.
run --format json --dry-run --from Humpty --to Dumpty test-json/humpty-dumpty.txt

# JSON output for actual replacement.
run --format json --from Humpty --to Dumpty test-json/humpty-dumpty.txt

# JSON output for undo (pass directory so undo can find .orig files).
run --format json --undo --full --from Humpty --to Dumpty test-json

# JSON output for clean-backups (no backups remain after undo, so should be 0).
run --format json --clean-backups test-json


# Regex and capturing groups.

cp -a original test-regex

# Create test file with figures
echo 'See figure 1 and figure 23 for details.' > test-regex/figures.txt

# Test capturing group replacement
run --from 'figure ([0-9]+)' --to 'Figure \1' test-regex/figures.txt

cat test-regex/figures.txt


# Literal mode.

cp -a original test-literal

# Create file with regex special chars
echo 'Match foo.bar and fooXbar here.' > test-literal/special.txt

# Without --literal: . matches any char (matches both foo.bar and fooXbar)
run --from 'foo.bar' --to 'REPLACED' test-literal/special.txt

cat test-literal/special.txt

# Reset and test with --literal (only exact match)
cp -a original test-literal2
echo 'Match foo.bar and fooXbar here.' > test-literal2/special.txt

run --literal --from 'foo.bar' --to 'REPLACED' test-literal2/special.txt

cat test-literal2/special.txt


# At-once mode (multiline patterns).

cp -a original test-atonce

# Create multiline test file
printf 'start\nmiddle\nend\n' > test-atonce/multiline.txt

# Default (line-by-line) won't match across lines
run -n --from 'start.*end' --to 'REPLACED' test-atonce/multiline.txt

# With --at-once and --dotall, pattern spans lines
run --at-once --dotall --from 'start.*end' --to 'REPLACED' test-atonce/multiline.txt

cat test-atonce/multiline.txt


# Parse-only mode.

run -t --from 'foo' --to 'bar'

run -t -p patterns-misc


# Stdin/stdout mode.
# Note: We use PYTHONUNBUFFERED to ensure deterministic output order between stdout and stderr

PYTHONUNBUFFERED=1 bash -c 'echo "foo bar foo" | uv run repren --from foo --to bar'

PYTHONUNBUFFERED=1 bash -c 'echo "figure 1 and figure 2" | uv run repren --from "figure ([0-9]+)" --to "Fig. \1"'


# Quiet mode.

cp -a original test-quiet

run -q --from Humpty --to Dumpty test-quiet/humpty-dumpty.txt

# Verify changes were made silently
diff original/humpty-dumpty.txt test-quiet/humpty-dumpty.txt || expect_error


# Error cases.

run --from '[invalid(regex' --to 'bar' original || expect_error


# Skill instructions (print mode - safe to test without side effects).

run --skill | head -5


# Claude skill installation tests.

# Test project-local install (creates .claude/skills/repren/)
run --install-skill --agent-base=./.claude

# Verify project skill file exists and has content
test -f .claude/skills/repren/SKILL.md && echo "Project skill file created"
grep -q "repren" .claude/skills/repren/SKILL.md && echo "Project skill content verified"

# Test global install (uses temp directory to avoid polluting user's home)
mkdir -p test-home
HOME_BACKUP="$HOME"
HOME="$(pwd)/test-home"
export HOME

run --install-skill

# Verify global skill file exists and has content
test -f test-home/.claude/skills/repren/SKILL.md && echo "Global skill file created"
grep -q "repren" test-home/.claude/skills/repren/SKILL.md && echo "Global skill content verified"

# Restore HOME and clean up test directories
HOME="$HOME_BACKUP"
export HOME
rm -rf test-home
rm -rf .claude


# File collision handling (rename to existing file).

cp -a original test-collision

# Create a file that would conflict with the rename target
touch test-collision/dumpty-dumpty.txt

# Rename should handle collision (add numeric suffix or similar)
run --renames --from humpty --to dumpty test-collision

ls_portable test-collision | grep dumpty


# TODO: More test coverage:
# - CamelCase and whole word support.
# - Large stress test (rename a variable in a large source package and recompile).

# Leave files installed in case it's helpful to debug anything.

# --- End of tests ---
