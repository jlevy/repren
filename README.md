repren
======

Multi-pattern string replacement and file renaming

Repren is a simple utility for rewriting text file contents according to a set
of regular expression patterns, or to rename or move files according to
patterns on file paths, or both. Essentially, it is a general-purpose,
brute-force text file refactoring tool. For example, repren could rename all
occurrences of a class name in Java source file, while simultaneously renaming
the Java files with that name. It's more powerful than `perl -pie`, `rpl`,
`sed`, and the like since it can also rename files, and has features like group
renamings (e.g. rename "foo" as "bar", and "bar" as "foo" at once, without
requiring a temporary intermediate rename).

It reads entire files into memory, without streaming -- so won't work on
enormous files.

Applies recursively to file paths, if supplied. Otherwise, reads from stdin and
writes to stdout.

Notes:

- Patterns must be supplied in a text file, of the form <regex><tab><replacement>,
  one per line. Empty lines and `#`-prefixed comments are OK.
- Replacements may include back substitutions from regular expressions (\1, \2,
  etc.).
- Replacements are applied as a group, so it's possible to swap or otherwise change
  names, variables, etc. in ways that would require multiple steps if done one
  `sed` command at at a time.
- If two patterns have matches that overlap, only one replacement is applied,
  with preference to the pattern appearing first in the patterns file.
- The same logic applies filenames, with patterns applied to the full file path
  (use caution on absolute path arguments!), and parent directories created as
  needed.
- Files are not clobbered by renames. If two files are renamed to the same
  target, one will have a numeric suffix (".1", ".2", etc.).
- Files are created then renamed, so no output file will ever be partial, even
  in case of errors.
- Backups are created of all modified files, with the suffix ".orig".
