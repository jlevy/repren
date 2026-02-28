---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Replacement Basics

## R1: Dry run shows intended rewrite

```console
$ cp -r fixtures/original test1 && repren -n --from Humpty --to Dumpty test1/humpty-dumpty.txt
Dry run: No files will be changed
Using 1 patterns:
  'Humpty' -> 'Dumpty'
Found 1 files in: test1/humpty-dumpty.txt
- modify: test1/humpty-dumpty.txt: 3 matches
Read 1 files (513 chars), found 3 matches (0 skipped due to overlaps)
Dry run: Would have changed 1 files (1 rewritten and 0 renamed)
? 0
```

## R2: Dry run does not modify files

```console
$ diff -rq fixtures/original test1
```

## R3: Case-sensitive no-op replacement

```console
$ repren --from humpty --to dumpty test1/humpty-dumpty.txt
Using 1 patterns:
  'humpty' -> 'dumpty'
Found 1 files in: test1/humpty-dumpty.txt
Read 1 files (513 chars), found 0 matches (0 skipped due to overlaps)
Changed 0 files (0 rewritten and 0 renamed)
? 0
```

## R4: Actual replacement rewrites and creates backup

```console
$ repren --from Humpty --to Dumpty test1/humpty-dumpty.txt
Using 1 patterns:
  'Humpty' -> 'Dumpty'
Found 1 files in: test1/humpty-dumpty.txt
- modify: test1/humpty-dumpty.txt: 3 matches
Read 1 files (513 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ sed -n '1,5p' test1/humpty-dumpty.txt
Dumpty Dumpty smiled contemptuously. 'Of course you don't — till I tell you. I meant "there's a nice knock-down argument for you!"'
'But "glory" doesn't mean "a nice knock-down argument",' Alice objected.
'When I use a word,' Dumpty Dumpty said, in rather a scornful tone, 'it means just what I choose it to mean — neither more nor less.'
'The question is,' said Alice, 'whether you can make words mean so many different things.'
'The question is,' said Dumpty Dumpty, 'which is to be master — that's all.'
? 0
```

```console
$ test -f test1/humpty-dumpty.txt.orig && echo "backup exists"
backup exists
? 0
```

## R5: Backup files are skipped on directory traversal

```console
$ repren --from humpty --to dumpty test1
Using 1 patterns:
  'humpty' -> 'dumpty'
Skipped 1 file(s) ending in '.orig' (backup files are never processed)
Found 12 files in: test1
Read 12 files (3810 chars), found 0 matches (0 skipped due to overlaps)
Changed 0 files (0 rewritten and 0 renamed)
? 0
```
