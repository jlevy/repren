---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
patterns:
  SHA256: '[0-9a-f]{64}'
---

# Backup Cache-Lifecycle Internals

## C1: Full rewrite creates backup cache artifact plus transformed target

```console
$ cp -r fixtures/original cachecase && repren --full -i --from humpty --to dumpty cachecase
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
Found 12 files in: cachecase
- modify: cachecase/humpty-dumpty.txt: 3 matches
- rename: cachecase/humpty-dumpty.txt -> cachecase/dumpty-dumpty.txt
Read 12 files (3810 chars), found 3 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 1 renamed)
? 0
```

```console
$ find cachecase -maxdepth 1 -type f | sort
cachecase/dumpty-dumpty.txt
cachecase/humpty-dumpty.txt.orig
? 0
```

```console
$ head -1 cachecase/humpty-dumpty.txt.orig && head -1 cachecase/dumpty-dumpty.txt
Humpty Dumpty smiled contemptuously. 'Of course you don't — till I tell you. I meant "there's a nice knock-down argument for you!"'
dumpty Dumpty smiled contemptuously. 'Of course you don't — till I tell you. I meant "there's a nice knock-down argument for you!"'
? 0
```

## C2: Backup and transformed files have distinct content hashes

```console
$ python -c "import hashlib,pathlib; f=pathlib.Path('fixtures/original/humpty-dumpty.txt').read_bytes(); b=pathlib.Path('cachecase/humpty-dumpty.txt.orig').read_bytes(); c=pathlib.Path('cachecase/dumpty-dumpty.txt').read_bytes(); fh=hashlib.sha256(f).hexdigest(); bh=hashlib.sha256(b).hexdigest(); ch=hashlib.sha256(c).hexdigest(); print('fixture_sha256='+fh); print('backup_sha256='+bh); print('current_sha256='+ch); print('backup_matches_fixture='+str(fh==bh).lower()); print('current_matches_backup='+str(ch==bh).lower())"
fixture_sha256=17b532c9190d20245924568ef3bcc5e357f22482a80d6fe75cb48855d80e502c
backup_sha256=17b532c9190d20245924568ef3bcc5e357f22482a80d6fe75cb48855d80e502c
current_sha256=10b24ed567ad3092ebc1f537ccd54ae812dce5923f3adb260b20540f86e0d8ea
backup_matches_fixture=true
current_matches_backup=false
? 0
```

## C3: Undo restores from backup cache artifact and removes transformed path

```console
$ repren --undo --full -i --from humpty --to dumpty cachecase
Using 1 patterns:
  'humpty' IGNORECASE -> 'dumpty'
- restore: cachecase/humpty-dumpty.txt.orig -> cachecase/humpty-dumpty.txt
Restored 1 file(s), skipped 0 with warnings
? 0
```

```console
$ find cachecase -maxdepth 1 -type f | sort
cachecase/humpty-dumpty.txt
? 0
```

```console
$ head -1 cachecase/humpty-dumpty.txt
Humpty Dumpty smiled contemptuously. 'Of course you don't — till I tell you. I meant "there's a nice knock-down argument for you!"'
? 0
```

## C4: Timestamp guard skips unsafe restore when backup is newer than target

```console
$ mkdir -p guard && printf 'backup\n' > guard/file.txt.orig && printf 'target\n' > guard/file.txt && touch -t 202601010101 guard/file.txt && touch -t 202601010102 guard/file.txt.orig && repren --undo --from NO --to NO guard
Using 1 patterns:
  'NO' -> 'NO'
- skip: guard/file.txt.orig: backup is newer than current file
Restored 0 file(s), skipped 1 with warnings
? 0
```

```console
$ cat guard/file.txt && cat guard/file.txt.orig
target
backup
? 0
```
