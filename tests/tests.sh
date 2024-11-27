#!/bin/bash

# Test script. Output of this script can be saved and compared to test for regressions.
# Double-spacing between commands here makes the script output easier to read.

# We turn on exit on error, so that any status code changes cause a test failure.
set -e -o pipefail

prog_name=repren
base_dir=`dirname $0`
prog=$base_dir/../repren/repren.py

args=
#args=--debug

run() {
  $prog $args "$@"
}

# A trick to test for error conditions.
expect_error() {
  echo "(got expected error: status $?)"
}

# A trick to do ls portably, showing just files and types.
ls_portable() {
  ls -1F "$@"
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


# Moving files.

# TODO: Fix this.
# cp -a original test9
# run --renames --from stuff/trees --to another-dir test9


# TODO: More test coverage:
# - Regex and capturing groups.
# - CamelCase and whole word support.
# - Large stress test (rename a variable in a large source package and recompile).

# Leave files installed in case it's helpful to debug anything.

# --- End of tests ---
