---
sandbox: true
before: |
  cp -r $TRYSCRIPT_TEST_DIR/fixtures/. fixtures/
---

# Pattern Files and Case Preservation

## P1: Pattern-file content replacements

```console
$ cp -r fixtures/original test4 && repren -p fixtures/patterns-misc test4
Using 5 patterns:
  'humpty' -> 'dumpty'
  'dumpty' -> 'humpty'
  'beech' -> 'BEECH'
  'Asia' -> 'Asia!'
  'Europe' -> 'Europe!'
Found 12 files in: test4
- modify: test4/stuff/trees/beech.txt: 8 matches
- modify: test4/stuff/trees/maple.txt: 3 matches
- modify: test4/stuff/trees/oak.txt: 3 matches
Read 12 files (3810 chars), found 14 matches (0 skipped due to overlaps)
Changed 3 files (3 rewritten and 0 renamed)
? 0
```

```console
$ find test4/stuff/words -maxdepth 1 -type f | sort
test4/stuff/words/.hidden.txt
test4/stuff/words/Asia
test4/stuff/words/Europe
test4/stuff/words/Mexico
test4/stuff/words/United
test4/stuff/words/genetic
test4/stuff/words/genus
test4/stuff/words/oak
test4/stuff/words/second
? 0
```

```console
$ sed -n '1,2p' test4/stuff/trees/beech.txt && echo
Beech (Fagus) is a genus of deciduous trees in the family Fagaceae, native to temperate Europe!, Asia! and North America. Recent classification systems of the genus recognize ten to thirteen species in two distinct subgenera, Engleriana and Fagus.[1][2] The Engleriana subgenus is found only in East Asia!, and is notably distinct from the Fagus subgenus in that these BEECHes are low-branching trees, often made up of several major trunks with yellowish bark. Further differentiating characteristics include the whitish bloom on the underside of the leaves, the visible tertiary leaf veins, and a long, smooth cupule-peduncle. Fagus japonica, Fagus engleriana, and the species F. okamotoi, proposed by the bontanist Chung-Fu Shen in 1992, comprise this subgenus.[2] The better known Fagus subgenus BEECHes are high-branching with tall, stout trunks and smooth silver-grey bark. This group includes Fagus sylvatica, Fagus grandifolia, Fagus crenata, Fagus lucida, Fagus longipetiolata, and Fagus hayatae.[2] The classification of the Europe!an BEECH, Fagus sylvatica is complex, with a variety of different names proposed for different species and subspecies within this region (for example Fagus taurica, Fagus orientalis, and Fagus moesica[3]). Research suggests that BEECHes in Eurasia differentiated fairly late in evolutionary history, during the Miocene. The populations in this area represent a range of often overlapping morphotypes, though genetic analysis does not clearly support separate species.[4]
? 0
```

## P2: Pattern-file full mode (content + renames)

```console
$ cp -r fixtures/original test5 && repren --full -i -p fixtures/patterns-misc test5
Using 5 patterns:
  'humpty' IGNORECASE -> 'dumpty'
  'dumpty' IGNORECASE -> 'humpty'
  'beech' IGNORECASE -> 'BEECH'
  'Asia' IGNORECASE -> 'Asia!'
  'Europe' IGNORECASE -> 'Europe!'
Found 12 files in: test5
- modify: test5/humpty-dumpty.txt: 6 matches
- rename: test5/humpty-dumpty.txt -> test5/dumpty-humpty.txt
- modify: test5/stuff/trees/beech.txt: 10 matches
- rename: test5/stuff/trees/beech.txt -> test5/stuff/trees/BEECH.txt
- modify: test5/stuff/trees/maple.txt: 3 matches
- modify: test5/stuff/trees/oak.txt: 3 matches
- rename: test5/stuff/words/Asia -> test5/stuff/words/Asia!
- rename: test5/stuff/words/Europe -> test5/stuff/words/Europe!
Read 12 files (3810 chars), found 22 matches (0 skipped due to overlaps)
Changed 6 files (4 rewritten and 4 renamed)
? 0
```

```console
$ find test5/stuff -maxdepth 2 -type f | sort
test5/stuff/trees/BEECH.txt
test5/stuff/trees/beech.txt.orig
test5/stuff/trees/maple.txt
test5/stuff/trees/maple.txt.orig
test5/stuff/trees/oak.txt
test5/stuff/trees/oak.txt.orig
test5/stuff/words/.hidden.txt
test5/stuff/words/Asia!
test5/stuff/words/Asia.orig
test5/stuff/words/Europe!
test5/stuff/words/Europe.orig
test5/stuff/words/Mexico
test5/stuff/words/United
test5/stuff/words/genetic
test5/stuff/words/genus
test5/stuff/words/oak
test5/stuff/words/second
? 0
```

## P3: Preserve-case rotation over full tree

```console
$ cp -r fixtures/original test6 && repren --full --preserve-case -p fixtures/patterns-rotate-abc test6
Using 6 patterns:
  'A' -> 'B'
  'a' -> 'b'
  'B' -> 'C'
  'b' -> 'c'
  'C' -> 'A'
  'c' -> 'a'
Found 12 files in: test6
- modify: test6/humpty-dumpty.txt: 40 matches
- modify: test6/stuff/trees/beech.txt: 180 matches
- rename: test6/stuff/trees/beech.txt -> test6/stuff/trees/ceeah.txt
- modify: test6/stuff/trees/maple.txt: 43 matches
- rename: test6/stuff/trees/maple.txt -> test6/stuff/trees/mbple.txt
- modify: test6/stuff/trees/oak.txt: 161 matches
- rename: test6/stuff/trees/oak.txt -> test6/stuff/trees/obk.txt
- rename: test6/stuff/words/Asia -> test6/stuff/words/Bsib
- rename: test6/stuff/words/Mexico -> test6/stuff/words/Mexiao
- rename: test6/stuff/words/genetic -> test6/stuff/words/genetia
- rename: test6/stuff/words/oak -> test6/stuff/words/obk
- rename: test6/stuff/words/second -> test6/stuff/words/seaond
Read 12 files (3810 chars), found 424 matches (0 skipped due to overlaps)
Changed 9 files (4 rewritten and 8 renamed)
? 0
```

## P4: Two more rotations return to original content

```console
$ repren --full --preserve-case -p fixtures/patterns-rotate-abc test6 && repren --full --preserve-case -p fixtures/patterns-rotate-abc test6 && find test6 -name '*.orig' -delete && diff -rq fixtures/original test6
Using 6 patterns:
  'A' -> 'B'
  'a' -> 'b'
  'B' -> 'C'
  'b' -> 'c'
  'C' -> 'A'
  'c' -> 'a'
Skipped 9 file(s) ending in '.orig' (backup files are never processed)
Found 12 files in: test6
- modify: test6/humpty-dumpty.txt: 40 matches
- modify: test6/stuff/trees/ceeah.txt: 180 matches
- rename: test6/stuff/trees/ceeah.txt -> test6/stuff/trees/aeebh.txt
- modify: test6/stuff/trees/mbple.txt: 43 matches
- rename: test6/stuff/trees/mbple.txt -> test6/stuff/trees/mcple.txt
- modify: test6/stuff/trees/obk.txt: 161 matches
- rename: test6/stuff/trees/obk.txt -> test6/stuff/trees/ock.txt
- rename: test6/stuff/words/Bsib -> test6/stuff/words/Csic
- rename: test6/stuff/words/Mexiao -> test6/stuff/words/Mexibo
- rename: test6/stuff/words/genetia -> test6/stuff/words/genetib
- rename: test6/stuff/words/obk -> test6/stuff/words/ock
- rename: test6/stuff/words/seaond -> test6/stuff/words/sebond
Read 12 files (3810 chars), found 424 matches (0 skipped due to overlaps)
Changed 9 files (4 rewritten and 8 renamed)
Using 6 patterns:
  'A' -> 'B'
  'a' -> 'b'
  'B' -> 'C'
  'b' -> 'c'
  'C' -> 'A'
  'c' -> 'a'
Skipped 17 file(s) ending in '.orig' (backup files are never processed)
Found 12 files in: test6
- modify: test6/humpty-dumpty.txt: 40 matches
- modify: test6/stuff/trees/aeebh.txt: 180 matches
- rename: test6/stuff/trees/aeebh.txt -> test6/stuff/trees/beech.txt
- modify: test6/stuff/trees/mcple.txt: 43 matches
- rename: test6/stuff/trees/mcple.txt -> test6/stuff/trees/maple.txt
- modify: test6/stuff/trees/ock.txt: 161 matches
- rename: test6/stuff/trees/ock.txt -> test6/stuff/trees/oak.txt
- rename: test6/stuff/words/Csic -> test6/stuff/words/Asia
- rename: test6/stuff/words/Mexibo -> test6/stuff/words/Mexico
- rename: test6/stuff/words/genetib -> test6/stuff/words/genetic
- rename: test6/stuff/words/ock -> test6/stuff/words/oak
- rename: test6/stuff/words/sebond -> test6/stuff/words/second
Read 12 files (3810 chars), found 424 matches (0 skipped due to overlaps)
Changed 9 files (4 rewritten and 8 renamed)
? 0
```
