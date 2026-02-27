---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Rename and Full Mode

## N1: Dry-run rename-only

```console
$ cp -r fixtures/original test2 && repren -n --renames --from humpty --to dumpty test2
Dry run: No files will be changed
Using 1 patterns:
  'humpty' -> 'dumpty'
Found 12 files in: test2
- rename: test2/humpty-dumpty.txt -> test2/dumpty-dumpty.txt
Read 1 files (0 chars), found 0 matches (0 skipped due to overlaps)
Dry run: Would have changed 1 files (0 rewritten and 1 renamed)
? 0
```

## N2: Rename-only mutation

```console
$ repren --renames --from humpty --to dumpty test2
Using 1 patterns:
  'humpty' -> 'dumpty'
Found 12 files in: test2
- rename: test2/humpty-dumpty.txt -> test2/dumpty-dumpty.txt
Read 1 files (0 chars), found 0 matches (0 skipped due to overlaps)
Changed 1 files (0 rewritten and 1 renamed)
? 0
```

```console
$ find test2 -maxdepth 2 -type f | sort
test2/dumpty-dumpty.txt
? 0
```

## N3: Full mode rewrites and renames

```console
$ cp -r fixtures/original test3 && repren --full -i --from humpty --to dumpty test3
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
Found 12 files in: test3
- modify: test3/humpty-dumpty.txt: 3 matches
- rename: test3/humpty-dumpty.txt -> test3/dumpty-dumpty.txt
Read 12 files (3810 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 1 renamed)
? 0
```

```console
$ find test3 -maxdepth 2 -type f | sort
test3/dumpty-dumpty.txt
test3/humpty-dumpty.txt.orig
? 0
```

## N4: Path-based move across directories

```console
$ cp -r fixtures/original test-move && mkdir -p test-move/relocated && repren --renames --from 'stuff/trees' --to 'relocated' test-move
Using 1 patterns:
  'stuff/trees' -> 'relocated'
Found 12 files in: test-move
- rename: test-move/stuff/trees/beech.txt -> test-move/relocated/beech.txt
- rename: test-move/stuff/trees/maple.txt -> test-move/relocated/maple.txt
- rename: test-move/stuff/trees/oak.txt -> test-move/relocated/oak.txt
Read 3 files (0 chars), found 0 matches (0 skipped due to overlaps)
Changed 3 files (0 rewritten and 3 renamed)
? 0
```

```console
$ find test-move -maxdepth 3 -type f | sort
test-move/humpty-dumpty.txt
test-move/relocated/beech.txt
test-move/relocated/maple.txt
test-move/relocated/oak.txt
test-move/stuff/words/.hidden.txt
test-move/stuff/words/Asia
test-move/stuff/words/Europe
test-move/stuff/words/Mexico
test-move/stuff/words/United
test-move/stuff/words/genetic
test-move/stuff/words/genus
test-move/stuff/words/oak
test-move/stuff/words/second
? 0
```
