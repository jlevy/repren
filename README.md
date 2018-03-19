# repren

![But call me repren for short](images/awkward-150.jpg)

## Rename anything

Repren is a simple but flexible command-line tool for rewriting file contents
according to a set of regular expression patterns, and to rename or move files
according to patterns. Essentially, it is a general-purpose, brute-force text
file refactoring tool. For example, repren could rename all occurrences of
certain class and variable names in a set of Java source files, while
simultaneously renaming the Java files according to the same pattern. It's more
powerful than usual options like `perl -pie`, `rpl`, or `sed`:

- It can do search-and-replace, file renaming, or both.
- It allows file renaming on full paths, including moving files, creating directories, or rewriting directory hierarchies.
- It supports fully expressive regular expressions, with capturing groups and back substitutions.
- It performs simultaneous group renamings, i.e. rename "foo" as "bar", and "bar" as "foo"
  at once, without requiring a temporary intermediate rename.
- It is careful. It has a nondestructive mode, and prints clear stats on its
  changes. It leaves backups. File operations are done atomically, so
  interruptions never leave a previously existing file truncated or partly
  edited.
- It supports helpful variations like an option to replace on word breaks, so you
  avoid splitting a word, and "case-preserving" renames that let you find and rename
  identifiers with case variants (lowerCamel, UpperCamel, lower_underscore, and
  UPPER_UNDERSCORE) consistently.
- It has this nice documentaion!

## Usage

Run `repren --help` for full usage and flags.

If file paths are provided, repren replaces those files in place, leaving a
backup with extension ".orig". If directory paths are provided, it applies
replacements recursively to all files in the supplied paths that are not in the
exclude pattern. If no arguments are supplied, it reads from stdin and writes
to stdout.

## Alternatives

Aren't there standard tools for this already?

It's a bit surprising, but not really.
Getting the features right is a bit tricky, I guess.
The [standard](http://stackoverflow.com/questions/11392478/how-to-replace-a-string-in-multiple-files-in-linux-command-line/29191549)
[answers](http://stackoverflow.com/questions/6840332/rename-multiple-files-by-replacing-a-particular-pattern-in-the-filenames-using-a)
like *sed*, *perl*, *awk*, *rename*, *Vim* macros, or even IDE refactoring
tools, often cover specific cases, but tend to be error-prone or not offer specific features you probably want.
Things like nondestructive mode, file renaming as well as search/replace, multiple simultaneous renames/swaps, or renaming enclosing parent directories.
Also many of these vary by platform, which adds to the corner cases.
Inevitably you end up digging through the darker corners of some man page or writing ugly scripts that would scare your mother.

## Installation

No dependencies except Python 2.7+. It's easiest to install with pip (using sudo if desired):

    pip install repren

Or, since it's just one file, you can copy the
[repren](https://raw.githubusercontent.com/jlevy/repren/master/repren)
script somewhere (perhaps within your own project) and make it executable.


## Try it

Let's try a simple replacement in my working directory (which has a few random source
files):

    bash-3.2$ repren --from frobinator-server --to glurp-server --full --dry-run .
    Dry run: No files will be changed
    Using 1 patterns:
      'frobinator-server' -> 'glurp-server'
    Found 102 files in: .
    - modify: ./site.yml: 1 matches
    - rename: ./roles/frobinator-server/defaults/main.yml -> ./roles/glurp-server/defaults/main.yml
    - rename: ./roles/frobinator-server/files/deploy-frobinator-server.sh -> ./roles/glurp-server/files/deploy-frobinator-server.sh
    - rename: ./roles/frobinator-server/files/install-graphviz.sh -> ./roles/glurp-server/files/install-graphviz.sh
    - rename: ./roles/frobinator-server/files/frobinator-purge-old-deployments -> ./roles/glurp-server/files/frobinator-purge-old-deployments
    - rename: ./roles/frobinator-server/handlers/main.yml -> ./roles/glurp-server/handlers/main.yml
    - rename: ./roles/frobinator-server/tasks/main.yml -> ./roles/glurp-server/tasks/main.yml
    - rename: ./roles/frobinator-server/templates/frobinator-webservice.conf.j2 -> ./roles/glurp-server/templates/frobinator-webservice.conf.j2
    - rename: ./roles/frobinator-server/templates/frobinator-webui.conf.j2 -> ./roles/glurp-server/templates/frobinator-webui.conf.j2
    Read 102 files (190382 chars), found 2 matches (0 skipped due to overlaps)
    Dry run: Would have changed 2 files, including 0 renames

That was a dry run, so if it looks good, it's easy to repeat that a second time, dropping the `--dry-run` flag.
If this is in git, we'd do a git diff to verify, test, then commit it all.
If we messed up, there are still .orig files present.

## Patterns

Patterns can be supplied using the `--from` and `--to` syntax above, but that only works for a single pattern.

In general, you can perform multiple simultaneous replacements by putting them in a _patterns file_.
Each line consists of a regular expression and replacement. For example:

    # Sample pattern file
    frobinator<tab>glurp
    WhizzleStick<tab>AcmeExtrudedPlasticFunProvider
    figure ([0-9+])<tab>Figure \1

(Where `<tab>` is an actual tab character.)

Empty lines and #-prefixed comments are ignored. Capturing groups and back substitutions (such as \1 above) are supported. 

## Examples

    # Here `patfile` is a patterns file.
    # Rewrite stdin:
    repren -p patfile < input > output

    # Shortcut with a single pattern replacement (replace foo with bar):
    repren --from foo --to bar < input > output

    # Rewrite a few files in place, also requiring matches be on word breaks:
    repren -p patfile --word-breaks myfile1 myfile2 myfile3

    # Rewrite whole directory trees. Since this is a big operation, we use
    # `-n` to do a dry run that only prints what would be done:
    repren -n -p patfile --word-breaks --full mydir1

    # Now actually do it:
    repren -p patfile --word-breaks --full mydir1

    # Same as above, for all case variants:
    repren -p patfile --word-breaks --preserve-case --full mydir1

## Notes

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

## Contributing

Contributions and issues welcome! Do understand and run the (manual) regression tests,
review the output, and commit the clean log changes if you submit a PR. (And mention this
in the PR.)

## License

Apache 2.
