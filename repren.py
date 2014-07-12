#!/usr/bin/env python

r'''
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
'''

# Author: jlevy
# Created: 2014-07-09

from __future__ import print_function
import re, sys, os, shutil, optparse, bisect

VERSION = "0.2.1"
DESCRIPTION = "repren: Multi-pattern string replacement and file renaming"

BACKUP_SUFFIX = ".orig"
DEFAULT_OMIT_PAT = r"\."

def log(source_name, msg):
  if source_name:
    msg = "%s: %s" % (source_name, msg)
  print(msg, file=sys.stderr)

def fail(msg):
  print("error: " + msg, file=sys.stderr)
  sys.exit(1)


global _tally_files, _tally_chars, _tally_replacements, _tally_files_written, _tally_renames
_tally_files = 0
_tally_chars = 0
_tally_replacements = 0
_tally_files_written = 0
_tally_renames = 0


## String matching

def _overlap(match1, match2):
  return match1.start() < match2.end() and match2.start() < match1.end()

def _sort_drop_overlaps(matches, source_name=None):
  '''Select and sort a set of disjoint intervals, omitting ones that overlap.'''
  non_overlaps = []
  starts = []
  for (match, replacement) in matches:
    index = bisect.bisect_left(starts, match.start())
    if index > 0:
      (prev_match, _) = non_overlaps[index - 1]
      if _overlap(prev_match, match):
        log(source_name, "Skipping overlapping match '%s' of '%s' that overlaps '%s' of '%s' on its left" %
          (match.group(), match.re.pattern, prev_match.group(), prev_match.re.pattern))
        continue
    if index < len(non_overlaps):
      (next_match, _) = non_overlaps[index]
      if _overlap(next_match, match):
        log(source_name, "Skipping overlapping match '%s' of '%s' that overlaps '%s' of '%s' on its right" %
          (match.group(), match.re.pattern, next_match.group(), next_match.re.pattern))
        continue
    starts.insert(index, match.start())
    non_overlaps.insert(index, (match, replacement))
  return non_overlaps

def _apply_replacements(input, matches):
  out = []
  pos = 0
  for (match, replacement) in matches:
    out.append(input[pos:match.start()])
    out.append(match.expand(replacement))
    pos = match.end()
  out.append(input[pos:])
  return "".join(out)

def multi_replace(input, patterns, source_name=None, is_path=False):
  '''Replace all occurrences in the input given a list of patterns (regex,
  replacement), simultaneously, so that no replacement affects any other. E.g.
  { xxx -> yyy, yyy -> xxx } or { xxx -> yyy, y -> z } are possible. If matches
  overlap, one is selected, with matches appearing earlier in the list of
  patterns preferred.
  '''
  matches = []
  for (regex, replacement) in patterns:
    for match in regex.finditer(input):
      matches.append((match, replacement))
  if len(matches) > 0 and source_name:
    log(source_name, "%s matches" % len(matches))
  new_matches = _sort_drop_overlaps(matches, source_name=source_name)

  global _tally_files, _tally_chars, _tally_replacements
  if not is_path:
    _tally_files += 1
    _tally_chars += len(input)
    _tally_replacements += len(new_matches)

  return _apply_replacements(input, new_matches)


## Case handling (only used for case-preserving magic)

# TODO: Could handle dash-separated names as well.

# FooBarBaz -> Foo, Bar, Baz
# XMLFooHTTPBar -> XML, Foo, HTTP, Bar
_camel_split_pat1 = re.compile("([^A-Z])([A-Z])")
_camel_split_pat2 = re.compile("([A-Z])([A-Z][^A-Z])")

_name_pat = re.compile(r"\w+")

def _split_name(name):
  '''Split a camel-case or underscore-formatted name into words. Return separator and words.'''
  if name.find("_") >= 0:
    return ("_", name.split("_"))
  else:
    temp = _camel_split_pat1.sub("\\1\t\\2", name)
    temp = _camel_split_pat2.sub("\\1\t\\2", temp)
    return ("", temp.split("\t"))

def _capitalize(word):
  return word[0].upper() + word[1:].lower()

def to_lower_camel(name):
  words = _split_name(name)[1]
  return words[0].lower() + "".join([_capitalize(word) for word in words[1:]])

def to_upper_camel(name):
  words = _split_name(name)[1]
  return "".join([_capitalize(word) for word in words])

def to_lower_underscore(name):
  words = _split_name(name)[1]
  return "_".join([word.lower() for word in words])

def to_upper_underscore(name):
  words = _split_name(name)[1]
  return "_".join([word.upper() for word in words])

def _transform_expr(expr, transform):
  return _name_pat.sub(lambda m: transform(m.group()), expr)

def all_case_variants(expr):
  '''Return all casing variations of an expression, replacing each name with
  lower- and upper-case camel-case and underscore style names, in fixed order.'''
  return [_transform_expr(expr, transform) for transform in [to_lower_camel, to_upper_camel, to_lower_underscore, to_upper_underscore]]


## File handling

def make_parent_dirs(path):
  '''Ensure parent directories of a file are created as needed.'''
  dir = os.path.dirname(path)
  if dir and not os.path.isdir(dir):
    os.makedirs(dir)
  return path

def move_file(source_path, dest_path, clobber=False):
   if not clobber:
     trailing_num = re.compile("(.*)[.]\d+$")
     i = 1
     while os.path.exists(dest_path):
       match = trailing_num.match(dest_path)
       if match:
         dest_path = match.group(1)
       dest_path = "%s.%s" % (dest_path, i)
       i = i + 1
   shutil.move(source_path, dest_path)

def transform_file(transform, source_path, dest_path, orig_suffix=BACKUP_SUFFIX, temp_suffix=".tmp", dry_run=False):
  '''Transform full contents of file at source_path in memory with specified
  function, writing dest_path atomically and keeping a backup. Source and
  destination may be the same path.'''
  global encoding
  with open(source_path, "rb") as input:
    contents = input.read()
    new_contents = transform(contents) if transform else contents
    modified = transform and new_contents != contents
    if modified or dest_path != source_path:
      if dest_path != source_path:
        log(None, "%s -> %s" % (source_path, dest_path))
      if not dry_run:
        orig_path = source_path + orig_suffix
        temp_path = dest_path + temp_suffix
        make_parent_dirs(temp_path)
        with open(temp_path, "wb") as output:
          output.write(new_contents)
        move_file(source_path, orig_path, clobber=True)
        move_file(temp_path, dest_path, clobber=False)

        global _tally_files_written, _tally_renames
        _tally_files_written += 1
        if dest_path != source_path:
          _tally_renames += 1

def rewrite_file(path, patterns, do_renames=False, do_contents=False, dry_run=False):
   dest_path = multi_replace(path, patterns, is_path=True) if do_renames else path
   transform = None
   if do_contents:
     transform = lambda contents: multi_replace(contents, patterns, source_name=path)
   transform_file(transform, path, dest_path, dry_run=dry_run)

def walk_files(paths, omit_pat=DEFAULT_OMIT_PAT):
  out = []
  omit_re = re.compile(omit_pat)
  for path in paths:
    if not os.path.exists(path):
      fail("path not found: %s" % path)
    if os.path.isfile(path):
      out.append(path)
    else:
      for (root, dirs, files) in os.walk(path):
        # Prune files that are excluded, and always prune backup files.
        out += [os.path.join(root, f) for f in files if not omit_re.match(f) and not f.endswith(BACKUP_SUFFIX)]
        # Prune subdirectories.
        dirs[:] = [d for d in dirs if not omit_re.match(d)]
  return out

def rewrite_files(root_paths, patterns, do_renames=False, do_contents=False, omit_pat=DEFAULT_OMIT_PAT, dry_run=False):
  log(None, "Using %s patterns" % len(patterns))
  paths = walk_files(root_paths, omit_pat=omit_pat)
  log(None, "Found %s files in %s" % (len(paths), root_paths))
  for path in paths:
    rewrite_file(path, patterns, do_renames=do_renames, do_contents=do_contents, dry_run=dry_run)


## Invocation

def parse_patterns(patterns_str, word_breaks=False, insensitive=False, preserve_case=False):
  patterns = []
  flags = re.I if insensitive else 0
  for line in patterns_str.splitlines():
    try:
      bits = line.split('\t')
      if line.strip().startswith("#"):
        continue
      elif line.strip() and len(bits) == 2:
        (regex, replacement) = bits
        pairs = []
        if preserve_case:
          pairs += zip(all_case_variants(regex), all_case_variants(replacement))
        if not (regex, replacement) in pairs:
          pairs.insert(0, (regex, replacement))
        for (regex_variant, replacement_variant) in pairs:
          if word_breaks:
            regex_variant = r'\b' + regex_variant + r'\b'
          patterns.append((re.compile(regex_variant, flags), replacement_variant))
      else:
        fail("invalid line in pattern file: %s" % bits)
    except Exception as e:
      raise e
      fail("error parsing pattern: %s: %s" % (e, bits))
  return patterns

# Remove excessive epilog formatting in optparse.
optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog

if __name__ == '__main__':
  USAGE = "%prog -p <pattern-file> {-f|-s|-F} [options] [path ...]"
  parser = optparse.OptionParser(usage=USAGE, description=DESCRIPTION, epilog="\n" + __doc__, version=VERSION)
  parser.add_option('-f', '--renames', help = 'do file renames (search/replace on full pathnames)', dest = 'do_renames', action = 'store_true')
  parser.add_option('-s', '--contents', help = 'do search/replace on file contents', dest = 'do_contents', action = 'store_true')
  parser.add_option('-F', '--full', help = 'do renames and search/replace', dest = 'do_full', action = 'store_true')
  parser.add_option('-i', '--insensitive', help = 'match case-insensitively', dest = 'insensitive', action = 'store_true')
  parser.add_option('-c', '--preserve-case', help = 'do case-preserving magic to transform all case variants (see below)', dest = 'preserve_case', action = 'store_true')
  parser.add_option('-b', '--word-breaks', help = 'require word breaks (regex \\b) around all matches', dest = 'word_breaks', action = 'store_true')
  parser.add_option('-p', '--patterns', help = 'file with replacement patterns (see below)', dest = 'patterns')
  parser.add_option('-x', '--exclude', help = 'file/directory name regex to exclude', dest = 'omit_pat', default = DEFAULT_OMIT_PAT)
  parser.add_option('-t', '--parse-only', help = 'parse patterns only', dest = 'parse_only', action = 'store_true')
  parser.add_option('-n', '--dry-run', help = 'dry run: just log matches without changing files', dest = 'dry_run', action = 'store_true')

  (options, root_paths) = parser.parse_args()

  options.do_renames = options.do_renames or options.do_full
  options.do_contents = options.do_contents or options.do_full

  if not options.patterns:
    parser.error("pattern file is required")
  if options.insensitive and options.preserve_case:
    parser.error("cannot use --insensitive and --preserve-case at once")
  if options.dry_run:
    log(None, "Dry run: no files will be changed")

  with open(options.patterns, "rb") as f:
    patterns = parse_patterns(f.read(), word_breaks=options.word_breaks, insensitive=options.insensitive, preserve_case=options.preserve_case)

  log(None, "Patterns:\n  " + "\n  ".join(["'%s' -> '%s'" % (regex.pattern, replacement) for (regex, replacement) in patterns]))

  if not options.parse_only:
    if len(root_paths) > 0:
      if not options.do_renames and not options.do_contents:
        parser.error('must specify whether to do renames or contents')
      rewrite_files(root_paths, patterns, do_renames=options.do_renames, do_contents=options.do_contents, dry_run=options.dry_run)
    else:
      print(multi_replace(sys.stdin.read(), patterns))

    log(None, "Read %s files (%s chars), found %s replacements, changed %s files (%s renames)" %
        (_tally_files, _tally_chars, _tally_replacements, _tally_files_written, _tally_renames))

