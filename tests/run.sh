#!/bin/bash

# Primitive but effective test harness for running command-line regression tests.
# This is all rather ugly but once this harness works, you only need to look at the
# tests file and occasionally edit the cleanup patterns below.

set -euo pipefail
trap "echo && echo 'Tests failed! See failure above.'" ERR

dir="$(cd `dirname $0`; pwd)"

full_log=$dir/golden-tests-full.log
baseline=$dir/golden-tests-expected.log
new_output=$dir/golden-tests-actual.log
final_diff=$dir/test.diff

echo Cleaning up...

rm -rf "$dir/tmp-dir"
cp -a $dir/work-dir $dir/tmp-dir
cd $dir/tmp-dir

echo "Running..."
echo "Platform and Python version:"
uname
uv run python -V

# Hackity hack:
# Remove per-run and per-platform details to allow easy comparison.
# Update these patterns as appropriate.
# Note we use perl not sed, so it works on Mac and Linux.
# The $|=1; is just for the impatient and ensures line buffering.
# We also use the cat trick below so it's possible to view the full log as it
# runs on stderr while writing to both logs.
$dir/golden-tests.sh 2>&1 \
  | tee $full_log \
  | tee >(cat 1>&2) \
  | perl -pe '$|=1; s/([a-zA-Z0-9._]+.py):[0-9]+/\1:xx/g' \
  | perl -pe '$|=1; s/File ".*\/([a-zA-Z0-9._]+.py)", line [0-9]*,/File "...\/\1", line __X,/g' \
  | perl -pe '$|=1; s/, line [0-9]*,/, line __X,/g' \
  | perl -pe '$|=1; s/partial.[a-z0-9]*/partial.__X/g' \
  | perl -pe '$|=1; s/ at 0x[0-9a-f]*/ at 0x__X/g' \
  | perl -pe '$|=1; s/[0-9.:T-]*Z/__TIMESTAMP/g' \
  | perl -pe '$|=1; s|/private/tmp/|/tmp/|g' \
  | perl -pe "\$|=1; s|$dir/tmp-dir|__TESTDIR__|g" \
  | perl -ne 'print unless /^pwd$/' \
  > $new_output

echo "Tests done."
echo
echo "Full log: $full_log"
echo "Actual output: $new_output"
echo "Expected output: $baseline"
echo
echo "Comparing actual vs expected..."

# Compare new output against the committed baseline
diff -u "$baseline" "$new_output" > $final_diff || true

if [ ! -s "$final_diff" ]; then
    echo
    echo "Success! No differences found."
    rm -f "$new_output"
    exit 0
else
    echo
    echo "Warning: Differences detected:"
    echo "----------------------------------------"
    cat $final_diff
    echo "----------------------------------------"
    echo
    echo "Tests did not pass!"
    echo "If the actual output is correct, update the expected baseline:"
    echo "  cp $new_output $baseline"

    exit 1
fi

