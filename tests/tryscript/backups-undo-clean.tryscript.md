---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Backup, Undo, and Cleanup Lifecycle

## B1: Full mode creates backup files

```console
$ cp -r fixtures/original test-backup && repren --full -i --from humpty --to dumpty test-backup
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
Found 12 files in: test-backup
- modify: test-backup/humpty-dumpty.txt: 3 matches
- rename: test-backup/humpty-dumpty.txt -> test-backup/dumpty-dumpty.txt
Read 12 files (3810 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 1 renamed)
? 0
```

```console
$ find test-backup -maxdepth 2 -type f | sort
test-backup/dumpty-dumpty.txt
test-backup/humpty-dumpty.txt.orig
? 0
```

## B2: Undo dry-run preview

```console
$ repren --undo -n --full -i --from humpty --to dumpty test-backup
Dry run: No files will be changed
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
- restore (dry-run): test-backup/humpty-dumpty.txt.orig -> test-backup/humpty-dumpty.txt
Would restore 1 file(s), skipped 0 with warnings
? 0
```

## B3: Undo restores original state

```console
$ repren --undo --full -i --from humpty --to dumpty test-backup && diff -rq fixtures/original test-backup
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
- restore: test-backup/humpty-dumpty.txt.orig -> test-backup/humpty-dumpty.txt
Restored 1 file(s), skipped 0 with warnings
? 0
```

## B4: Clean backups dry-run and apply

```console
$ repren --full -i --from humpty --to dumpty test-backup && repren --clean-backups -n test-backup && repren --clean-backups test-backup
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
Found 12 files in: test-backup
- modify: test-backup/humpty-dumpty.txt: 3 matches
- rename: test-backup/humpty-dumpty.txt -> test-backup/dumpty-dumpty.txt
Read 12 files (3810 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 1 renamed)
Dry run: No files will be changed
- remove (dry-run): test-backup/humpty-dumpty.txt.orig
Would remove 1 backup file(s)
- remove: test-backup/humpty-dumpty.txt.orig
Removed 1 backup file(s)
? 0
```

```console
$ find test-backup -name '*.orig' | wc -l | tr -d ' '
0
? 0
```

## B5: Custom backup suffix lifecycle

```console
$ cp -r fixtures/original test-suffix && repren --full -i --from humpty --to dumpty --backup-suffix .bak test-suffix && find test-suffix -name '*.bak' | wc -l | tr -d ' '
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
Found 12 files in: test-suffix
- modify: test-suffix/humpty-dumpty.txt: 3 matches
- rename: test-suffix/humpty-dumpty.txt -> test-suffix/dumpty-dumpty.txt
Read 12 files (3810 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 1 renamed)
1
? 0
```

```console
$ repren --clean-backups --backup-suffix .bak test-suffix && find test-suffix -name '*.bak' | wc -l | tr -d ' '
- remove: test-suffix/humpty-dumpty.txt.bak
Removed 1 backup file(s)
0
? 0
```
