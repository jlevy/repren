repren
======

### Multi-pattern string replacement and file renaming

**Your simple search-and-replace swiss army knife, when your editor, awk, perl,
or sed won't do. (Diesel power optional.)**

You know the drill. It's happened so may times. Since the acquisition,
Frobinators are now Glurps, and in version 3.0, WhizzleSticks are being
replaced by AcmeExtrudedPlasticFunProviders. But now there are 2000 Java files,
some JavaScript, maybe a little C++ and YAML, and of course documentation, that
all have to be updated at once. And there are a few different naming
conventions in each format. And the files and directories all have the old
names, too.

I really don't know why there isn't a single well-known tool for this already.
The standard tools like sed, awk, vim macros, or even IDE refactoring tools,
each only solve part of the problem. We've all cobbled together solutions
plenty of times. Well, here is a simple upgrade, that handles more of the
corner cases and won't have you writing throw-away bash scripts you'd be
embarrassed to show your mother, and digging through the dark corners of the
sed man page. It tries to cover a lot of use cases, and to do it simply.


### Synopsis

Repren is a simple utility for rewriting text file contents according to a set
of regular expression patterns, or to rename or move files according to
patterns on file paths, or both. Essentially, it is a general-purpose,
brute-force text file refactoring tool. For example, repren could rename all
occurrences of a class name in Java source file, while simultaneously renaming
the Java files with that name. It's more powerful than `perl -pie`, `rpl`,
`sed`, in particular since:

- It can also rename files, including moving files and creating directories.
- It performs group renamings (e.g. rename "foo" as "bar", and "bar" as "foo"
  at once, without requiring a temporary intermediate rename).
- It supports "magic" case-preserving renames that let you find and rename
  identifiers with case variants (lowerCamel, UpperCamel, lower_underscore, and
  UPPER_UNDERSCORE) consistently.

If file paths are provided, replaces those files in place, leaving a backup
with extension ".orig". If directory paths are provided, applies replacements
recursively to all files in the supplied paths that are not in the exclude
pattern. If no arguments supplied, reads from stdin and writes to stdout.

Limitations: It reads entire each file into memory, without streaming -- so
won't work on enormous files.

Notes:

- Patterns must be supplied in a text file, of the form <regex><tab><replacement>,
  one per line. Empty lines and `#`-prefixed comments are OK.
- As with sed, replacement text may include backreferences to groups within the
  regular expression, using the usual syntax: \1, \2, etc.
- Replacements are all matched on each input file, then all replaced, so it's
  possible to swap or otherwise change names in ways that would require
  multiple steps if done one replacement at at a time.
- If one pattern is a subset of another, consider if --word-breaks will help.
- If two patterns have matches that overlap, only one replacement is applied,
  with preference to the pattern appearing first in the patterns file.
- The case-preserving option works by adding all case variants to the pattern
  replacements, e.g. if the pattern file has foo_bar -> xxx_yyy, the
  replacements fooBar -> xxxYYY, FooBar -> XxxYyy, FOO_BAR -> XXX_YYY are also
  made. Assumes each pattern has one casing convention. (Plain ASCII names only.)
- The same logic applies filenames, with patterns applied to the full file path
  with slashes (e.g. my/path/to/filename) replaced and then and parent
  directories created as needed. (Use caution on absolute path arguments!)
- Files are never clobbered by renames. If a target already exists, or multiple
  files are renamed to the same target, numeric suffixes will be added to make
  the files distinct (".1", ".2", etc.).
- Files are created then renamed, so no output file will ever be partial, even
  in case of errors.
- Backups are created of all modified files, with the suffix ".orig".
- By default, recursive searching omits paths starting with ".". This may be
  adjusted with `--exclude`. Files ending in `.orig` are always ignored.


### Installation

One file. No dependencies. Tested on Python 2.7.
