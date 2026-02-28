---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Regex, Word Breaks, and Parse-Only

## X1: Regex capture-group replacement

```console
$ cp -r fixtures/original test-regex && printf 'See figure 1 and figure 23 for details.\n' > test-regex/figures.txt && repren --from 'figure ([0-9]+)' --to 'Figure \1' test-regex/figures.txt
Using 1 patterns:
  'figure ([0-9]+)' -> 'Figure \1'
Found 1 files in: test-regex/figures.txt
- modify: test-regex/figures.txt: 2 matches
Read 1 files (40 chars), found 2 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ cat test-regex/figures.txt
See Figure 1 and Figure 23 for details.
? 0
```

## X2: Word-break mode replaces whole words only

```console
$ mkdir -p wb && printf 'cat catalog Cat scat\n' > wb/word-breaks.txt && repren --word-breaks -i --from cat --to bat wb/word-breaks.txt
Using 1 patterns:
  '\bcat\b' IGNORECASE -> 'bat'
Found 1 files in: wb/word-breaks.txt
- modify: wb/word-breaks.txt: 2 matches
Read 1 files (21 chars), found 2 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ cat wb/word-breaks.txt
bat catalog bat scat
? 0
```

## X3: Parse-only emits parsed pattern set

```console
$ repren --parse-only --from 'foo([0-9]+)' --to 'bar\\1' fixtures/original/humpty-dumpty.txt
Using 1 patterns:
  'foo([0-9]+)' -> 'bar\\1'
? 0
```
