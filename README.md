repren
======

### Multi-pattern string replacement and file renaming

**A command-line search-and-replace swiss army knife**

You know the drill. In version 3.0, Frobinators are now Glurps, and
WhizzleSticks are being replaced by AcmeExtrudedPlasticFunProviders. But now
there are 2000 Java files, some JavaScript, a little C++ and YAML, and of
course documentation, that all have to be updated at once. And there are a few
different naming conventions in each format. And the files and directories all
have old names that should be changed, too.

I really don't know why there isn't a single well-known tool for this already.
The standard tools like sed, awk, vim macros, or even IDE refactoring tools,
each only solve part of the problem. Well, here is a simple upgrade, that
handles more of the corner cases and won't have you writing throw-away bash
scripts that would scare your mother, and digging through the dark corners of
the sed man page. It tries to cover a lot of use cases, and to do it simply.

### Installation

No dependencies except Python 2.7+. One file. Just download and run.

### Synopsis

Run `repren -h`:

    Usage: repren -p <pattern-file> [options] [path ...]

    repren: Multi-pattern string replacement and file renaming

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -p PATTERNS, --patterns=PATTERNS
                            file with replacement patterns (see below)
      -F, --full            do file renames and search/replace on file contents
      -f, --renames         do file renames only; do not modify file contents
      -l, --literal         use exact string matching, rather than regular
                            expresion matching
      -i, --insensitive     match case-insensitively
      -c, --preserve-case   do case-preserving magic to transform all case
                            variants (see below)
      -b, --word-breaks     require word breaks (regex \b) around all matches
      --exclude=EXCLUDE_PAT
                            file/directory name regex to exclude
      --at-once             transform each file's contents at once, instead of
                            line by line
      -t, --parse-only      parse and show patterns only
      -n, --dry-run         dry run: just log matches without changing files


Repren is a simple but flexible command-line tool for rewriting file contents
according to a set of regular expression patterns, and to rename or move files
according to patterns. Essentially, it is a general-purpose, brute-force text
file refactoring tool. For example, repren could rename all occurrences of
certain class and variable names a set of Java source files, while
simultaneously renaming the Java files according to the same pattern. It's more
powerful than usual options like `perl -pie`, `rpl`, or `sed`:

- It can also rename files, including moving files and creating directories.
- It performs group renamings (e.g. rename "foo" as "bar", and "bar" as "foo"
  at once, without requiring a temporary intermediate rename).
- It supports "magic" case-preserving renames that let you find and rename
  identifiers with case variants (lowerCamel, UpperCamel, lower_underscore, and
  UPPER_UNDERSCORE) consistently.
- It has a nondestructive mode, prints stats on its changes, and has a number
  of other useful options (see usage).
- It has this nice help page!

If file paths are provided, repren replaces those files in place, leaving a
backup with extension ".orig". If directory paths are provided, it applies
replacements recursively to all files in the supplied paths that are not in the
exclude pattern. If no arguments are supplied, it reads from stdin and writes
to stdout.

Patterns must be supplied in a text file, with one or more replacements consisting
of regular expression and replacement. For example:

    # Sample pattern file
    frobinator<tab>glurp
    WhizzleStick<tab>AcmeExtrudedPlasticFunProvider
    figure ([0-9+])<tab>Figure \1

(Where `<tab>` is an actual tab character.) Each line is a replacement.
Empty lines and #-prefixed comments are ignored.

Examples (here `patfile` is a patterns file):

    # Rewrite stdin:
    repren -p patfile < input > output

    # Rewrite a few files in place, also requiring matches be on word breaks:
    repren -p patfile --word-breaks myfile1 myfile2 myfile3

    # Rewrite whole directory trees. Since this is a big operation, we use
    # `-n` to do a dry run that only prints what would be done:
    repren -n -p patfile --word-breaks --full mydir1

    # Now actually do it:
    repren -p patfile --word-breaks --full mydir1

    # Same as above, for all case variants:
    repren -p patfile --word-breaks --preserve-case --full mydir1

Notes:

- As with sed, replacements are made line by line by default. Memory
  permitting, replacements may be done on entire files using `--at-once`.
- As with sed, replacement text may include backreferences to groups within the
  regular expression, using the usual syntax: \1, \2, etc.
- In the pattern file, both the regular expression and the replacement may
  contain the usual escapes `\n`, `\t`, etc. (To match a multi-line pattern,
  containing `\n`, you must must use `--at-once`.)
- Replacements are all matched on each input file, then all replaced, so it's
  possible to swap or otherwise change names in ways that would require
  multiple steps if done one replacement at at a time.
- If two patterns have matches that overlap, only one replacement is applied,
  with preference to the pattern appearing first in the patterns file.
- If one pattern is a subset of another, consider if `--word-breaks` will help.
- If patterns have special charaters, `--literal` may help.
- The case-preserving option works by adding all case variants to the pattern
  replacements, e.g. if the pattern file has foo_bar -> xxx_yyy, the
  replacements fooBar -> xxxYyy, FooBar -> XxxYyy, FOO_BAR -> XXX_YYY are also
  made. Assumes each pattern has one casing convention. (Plain ASCII names only.)
- The same logic applies to filenames, with patterns applied to the full file
  path with slashes replaced and then and parent directories created as needed,
  e.g. `my/path/to/filename` can be rewritten to `my/other/path/to/otherfile`.
  (Use caution and test with `-n`, especially when using absolute path
  arguments!)
- Files are never clobbered by renames. If a target already exists, or multiple
  files are renamed to the same target, numeric suffixes will be added to make
  the files distinct (".1", ".2", etc.).
- Files are created at a temporary location, then renamed, so original files are
  left intact in case of unexpected errors. File permissions are preserved.
- Backups are created of all modified files, with the suffix ".orig".
- By default, recursive searching omits paths starting with ".". This may be
  adjusted with `--exclude`. Files ending in `.orig` are always ignored.
- Data can be in any encoding, as it is treated as binary, and not interpreted
  in a specific encoding like UTF-8. This is less error prone in real-life
  situations where files have encoding inconsistencies. However, note the
  `--case-preserving` logic only handles casing conversions correctly for plain
  ASCII letters `[a-zA-Z]`.
