---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# JSON Output Contract

## J1: JSON walk-only

```console
$ cp -r fixtures/original test-json && repren --format json --walk-only test-json
{
  "operation": "walk",
  "paths": [
    "test-json/humpty-dumpty.txt",
    "test-json/stuff/trees/beech.txt",
    "test-json/stuff/trees/maple.txt",
    "test-json/stuff/trees/oak.txt",
    "test-json/stuff/words/Asia",
    "test-json/stuff/words/Europe",
    "test-json/stuff/words/Mexico",
    "test-json/stuff/words/United",
    "test-json/stuff/words/genetic",
    "test-json/stuff/words/genus",
    "test-json/stuff/words/oak",
    "test-json/stuff/words/second"
  ],
  "files_found": 12,
  "skipped_backups": 0
}
? 0
```

## J2: JSON dry-run replacement

```console
$ repren --format json --dry-run --from Humpty --to Dumpty test-json/humpty-dumpty.txt
{
  "operation": "replace",
  "dry_run": true,
  "patterns_count": 1,
  "files_found": 1,
  "chars_read": 513,
  "matches_found": 3,
  "matches_applied": 3,
  "files_changed": 1,
  "files_rewritten": 1,
  "files_renamed": 0
}
? 0
```

## J3: JSON actual replacement

```console
$ repren --format json --from Humpty --to Dumpty test-json/humpty-dumpty.txt
{
  "operation": "replace",
  "dry_run": false,
  "patterns_count": 1,
  "files_found": 1,
  "chars_read": 513,
  "matches_found": 3,
  "matches_applied": 3,
  "files_changed": 1,
  "files_rewritten": 1,
  "files_renamed": 0
}
? 0
```

## J4: JSON undo

```console
$ repren --format json --undo --full --from Humpty --to Dumpty test-json
{
  "operation": "undo",
  "dry_run": false,
  "restored": 1,
  "skipped": 0
}
? 0
```

## J5: JSON clean-backups

```console
$ repren --format json --clean-backups test-json
{
  "operation": "clean_backups",
  "dry_run": false,
  "removed": 0
}
? 0
```
