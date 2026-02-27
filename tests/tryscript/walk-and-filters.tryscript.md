---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Directory Walk and Include/Exclude Filters

## W1: Walk all files

```console
$ repren --walk-only fixtures/original
Found 12 files in: fixtures/original
- fixtures/original/humpty-dumpty.txt
- fixtures/original/stuff/trees/beech.txt
- fixtures/original/stuff/trees/maple.txt
- fixtures/original/stuff/trees/oak.txt
- fixtures/original/stuff/words/Asia
- fixtures/original/stuff/words/Europe
- fixtures/original/stuff/words/Mexico
- fixtures/original/stuff/words/United
- fixtures/original/stuff/words/genetic
- fixtures/original/stuff/words/genus
- fixtures/original/stuff/words/oak
- fixtures/original/stuff/words/second
? 0
```

## W2: Include text files only

```console
$ repren --walk-only --include='.*[.]txt$' fixtures/original
Found 4 files in: fixtures/original
- fixtures/original/humpty-dumpty.txt
- fixtures/original/stuff/trees/beech.txt
- fixtures/original/stuff/trees/maple.txt
- fixtures/original/stuff/trees/oak.txt
? 0
```

## W3: Exclude selected names

```console
$ repren --walk-only --exclude='beech|maple' fixtures/original
Found 11 files in: fixtures/original
- fixtures/original/humpty-dumpty.txt
- fixtures/original/stuff/trees/oak.txt
- fixtures/original/stuff/words/.hidden.txt
- fixtures/original/stuff/words/Asia
- fixtures/original/stuff/words/Europe
- fixtures/original/stuff/words/Mexico
- fixtures/original/stuff/words/United
- fixtures/original/stuff/words/genetic
- fixtures/original/stuff/words/genus
- fixtures/original/stuff/words/oak
- fixtures/original/stuff/words/second
? 0
```

## W4: Combined include and exclude

```console
$ repren --walk-only --include='A.*|M.*|oak' --exclude='Mex.*' fixtures/original
Found 3 files in: fixtures/original
- fixtures/original/stuff/trees/oak.txt
- fixtures/original/stuff/words/Asia
- fixtures/original/stuff/words/oak
? 0
```
