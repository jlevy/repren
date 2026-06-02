---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Advanced Option Semantics

## A1: `--literal` treats special regex chars as plain text

```console
$ mkdir -p adv && printf 'a.b\naXb\n' > adv/literal.txt && repren --literal --from 'a.b' --to ZZ adv/literal.txt
Using 1 patterns:
  'a\.b' -> 'ZZ'
Found 1 files in: adv/literal.txt
- modify: adv/literal.txt: 1 matches
Read 1 files (8 chars), found 1 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ cat adv/literal.txt
ZZ
aXb
? 0
```

## A2: `--dotall` still respects line-by-line default behavior

```console
$ printf 'A\n\nB\n' > adv/byline.txt && repren --dotall --from 'A.*B' --to JOIN adv/byline.txt
Using 1 patterns:
  'A.*B' DOTALL -> 'JOIN'
Found 1 files in: adv/byline.txt
Read 1 files (5 chars), found 0 matches (0 skipped due to overlaps)
Changed 0 files (0 rewritten and 0 renamed)
? 0
```

```console
$ cat adv/byline.txt
A

B
? 0
```

## A3: `--at-once` enables cross-line replacement with `--dotall`

```console
$ cp adv/byline.txt adv/atonce.txt && repren --dotall --at-once --from 'A.*B' --to JOIN adv/atonce.txt
Using 1 patterns:
  'A.*B' DOTALL -> 'JOIN'
Found 1 files in: adv/atonce.txt
- modify: adv/atonce.txt: 1 matches
Read 1 files (5 chars), found 1 matches (0 skipped due to overlaps)
Changed 1 files (1 rewritten and 0 renamed)
? 0
```

```console
$ cat adv/atonce.txt
JOIN
? 0
```

## A4: `--quiet` suppresses normal output on success

```console
$ printf 'one\n' > adv/quiet-ok.txt && repren --quiet --from one --to ONE adv/quiet-ok.txt > adv/quiet-ok.out 2> adv/quiet-ok.err && echo "out=$(wc -c < adv/quiet-ok.out | tr -d ' ') err=$(wc -c < adv/quiet-ok.err | tr -d ' ')" && cat adv/quiet-ok.txt
out=0 err=0
ONE
? 0
```

## A5: `--quiet` still emits error diagnostics

```console
$ set +e; repren --quiet > adv/quiet-fail.out 2> adv/quiet-fail.err; rc=$?; set -e; echo "rc=$rc out=$(wc -c < adv/quiet-fail.out | tr -d ' ')" && sed -n '1p' adv/quiet-fail.err
rc=2 out=0
usage: repren [-h] [--version] [--docs] [--from FROM_PAT] [--to TO_PAT] [-p PAT_FILE]
? 0
```

## A6: `--install-skill` with `--agent-base` writes both skill surfaces project-locally

```console
$ mkdir -p agentrepo && repren --install-skill --agent-base ./agentrepo/.claude >/dev/null
```

The skill is written to both the portable cross-agent location and the Claude mirror:

```console
$ find agentrepo -type f -name SKILL.md | sort
agentrepo/.agents/skills/repren/SKILL.md
agentrepo/.claude/skills/repren/SKILL.md
? 0
```

Frontmatter (stable top lines, version-independent):

```console
$ sed -n '1,3p' agentrepo/.claude/skills/repren/SKILL.md
---
name: repren
description: Performs simultaneous multi-pattern search-and-replace, file/directory renaming, and case-preserving refactoring across codebases. Use for bulk refactoring, global find-and-replace, or when user mentions repren, multi-file rename, or pattern-based transformations.
? 0
```

The skill uses a pinned zero-install runner, never an unpinned `@latest`:

```console
$ grep -q 'repren@latest' agentrepo/.claude/skills/repren/SKILL.md && echo found || echo none
none
? 0
```

```console
$ grep -Eq 'uvx repren@[0-9]' agentrepo/.claude/skills/repren/SKILL.md && echo pinned
pinned
? 0
```
