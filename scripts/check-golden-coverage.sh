#!/usr/bin/env bash
set -euo pipefail

# Quality gates for repren tryscript golden tests.
# Run from repository root.

EXIT_CODE=0
TESTS_DIR="tests/tryscript"

if [ ! -d "$TESTS_DIR" ]; then
  echo "ERROR: Missing $TESTS_DIR"
  exit 1
fi

echo "Checking anti-patterns..."
ELISIONS=$(grep -rn '^\.\.\.$' "$TESTS_DIR" 2>/dev/null || true)
if [ -n "$ELISIONS" ]; then
  echo "ERROR: Found bare ... elisions:"
  echo "$ELISIONS"
  EXIT_CODE=1
else
  echo "OK: no bare ... elisions"
fi

echo ""
echo "Checking required tryscript modules..."
REQUIRED_FILES=(
  help-errors.tryscript.md
  replacements.tryscript.md
  renames-and-full.tryscript.md
  patterns-and-case.tryscript.md
  walk-and-filters.tryscript.md
  backups-undo-clean.tryscript.md
  json-output.tryscript.md
  regex-wordbreaks.tryscript.md
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$TESTS_DIR/$file" ]; then
    echo "  MISSING: $file"
    EXIT_CODE=1
  else
    echo "  OK: $file"
  fi
done

echo ""
echo "Checking key CLI flag coverage..."
check_pattern() {
  local label="$1"
  local pattern="$2"
  local count
  count=$(grep -R -- "$pattern" "$TESTS_DIR" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -eq 0 ]; then
    echo "  MISSING: $label ($pattern)"
    EXIT_CODE=1
  else
    echo "  OK: $label ($count matches)"
  fi
}

check_pattern "help" "--help"
check_pattern "docs" "--docs"
check_pattern "skill" "--skill"
check_pattern "version" "--version"
check_pattern "single replacement" "--from"
check_pattern "single replacement target" "--to"
check_pattern "pattern file" "--patterns"
check_pattern "full mode" "--full"
check_pattern "rename mode" "--renames"
check_pattern "case-insensitive" "--insensitive"
check_pattern "preserve case" "--preserve-case"
check_pattern "word breaks" "--word-breaks"
check_pattern "walk only" "--walk-only"
check_pattern "dry run" "--dry-run"
check_pattern "include filter" "--include"
check_pattern "exclude filter" "--exclude"
check_pattern "parse only" "--parse-only"
check_pattern "undo" "--undo"
check_pattern "clean backups" "--clean-backups"
check_pattern "backup suffix" "--backup-suffix"
check_pattern "json mode" "--format json"

echo ""
FILE_COUNT=$(find "$TESTS_DIR" -name "*.tryscript.md" | wc -l | tr -d ' ')
FIXTURE_COUNT=$(find "$TESTS_DIR/fixtures" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "Tryscript files: $FILE_COUNT"
echo "Fixture files: $FIXTURE_COUNT"

exit "$EXIT_CODE"
