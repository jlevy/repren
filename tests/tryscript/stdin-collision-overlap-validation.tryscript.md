---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Stdin, Overlap, Collision, and Validation Paths

## S1: stdin replacement works in quiet mode

```console
$ printf 'line one\nline two\n' | repren --quiet --from line --to row
row one
row two
? 0
```

## S2: stdin supports cross-line replacement with `--dotall --at-once`

```console
$ printf 'A\n\nB\n' | repren --quiet --dotall --at-once --from 'A.*B' --to JOIN
JOIN
? 0
```

## S3: stdin rejects `--renames`

```console
$ set +e; out=$(printf 'x\n' | repren --renames --from x --to y 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: can't specify --renames on stdin; give filename arguments"
rc=2
repren: error: can't specify --renames on stdin; give filename arguments
? 0
```

## S4: stdin rejects `--dry-run`

```console
$ set +e; out=$(printf 'x\n' | repren --dry-run --from x --to y 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: can't specify --dry-run on stdin; give filename arguments"
rc=2
repren: error: can't specify --dry-run on stdin; give filename arguments
? 0
```

## S5: stdin rejects JSON mode

```console
$ set +e; out=$(printf 'x\n' | repren --format json --from x --to y 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: can't specify --format json on stdin; give filename arguments"
rc=2
repren: error: can't specify --format json on stdin; give filename arguments
? 0
```

## S6: overlapping matches are logged and only one replacement is applied

```console
$ mkdir -p ov && printf 'abcdef\n' > ov/input.txt && printf 'abc\tX\nbcd\tY\n' > ov/patterns.tsv && repren --patterns ov/patterns.tsv ov/input.txt
Using 2 patterns:
  'abc' -> 'X'
  'bcd' -> 'Y'
Found 1 files in: ov/input.txt
- ov/input.txt: Skipping overlapping match 'bcd' of 'bcd' that overlaps 'abc' of 'abc' on its left
- modify: ov/input.txt: 2 matches
Read 1 files (7 chars), found 1 matches (1 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ cat ov/input.txt
Xdef
? 0
```

## S7: rename collisions receive numeric suffixes

```console
$ mkdir -p col && printf 'one\n' > col/foo.txt && printf 'two\n' > col/bar.txt && printf 'foo\tshared\nbar\tshared\n' > col-pat.tsv && repren --renames --patterns col-pat.tsv col
Using 2 patterns:
  'foo' -> 'shared'
  'bar' -> 'shared'
Found 2 files in: col
- rename: col/bar.txt -> col/shared.txt
- rename: col/foo.txt -> col/shared.txt
Read 2 files (0 chars), found 0 matches (0 skipped due to overlaps)
Changed 2 files (0 rewritten and 2 renamed)
? 0
```

```console
$ find col -maxdepth 1 -type f | sort
col/shared.txt
col/shared.txt.1
? 0
```

```console
$ cat col/shared.txt col/shared.txt.1 | sort
one
two
? 0
```

## S8: undo skips when predicted renamed target is missing

```console
$ mkdir -p miss && printf 'orig\n' > miss/a.txt.orig && repren --undo --from a --to b miss
Using 1 patterns:
  'a' -> 'b'
- skip: miss/a.txt.orig: expected 'miss/b.txt' not found
Restored 0 file(s), skipped 1 with warnings
? 0
```

## S9: validation rejects `--patterns` combined with `--from/--to`

```console
$ set +e; out=$(repren --patterns fixtures/patterns-misc --from a --to b fixtures/original 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: cannot use both --patterns and --from/--to"
rc=2
repren: error: cannot use both --patterns and --from/--to
? 0
```

## S10: validation rejects `--insensitive` with `--preserve-case`

```console
$ set +e; out=$(repren --insensitive --preserve-case --from a --to b fixtures/original/humpty-dumpty.txt 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: cannot use --insensitive and --preserve-case at once"
rc=2
repren: error: cannot use --insensitive and --preserve-case at once
? 0
```

## S11: validation rejects `--clean-backups` with `--from/--to`

```console
$ set +e; out=$(repren --clean-backups --from a --to b fixtures/original 2>&1); rc=$?; set -e; echo "rc=$rc"; printf '%s\n' "$out" | grep -F "error: --clean-backups cannot be used with --patterns or --from/--to"
rc=2
repren: error: --clean-backups cannot be used with --patterns or --from/--to
? 0
```

## S12: rewrite works for file in current directory (no parent path component)

```console
$ mkdir -p cwdcase && (cd cwdcase && printf 'abc\n' > plain.txt && repren --quiet --from a --to A plain.txt && cat plain.txt)
Abc
? 0
```
