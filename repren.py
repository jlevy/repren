#!/usr/bin/env python

# Author: jlevy
# Created: 2014-07-09

from __future__ import print_function
import re, sys, os, shutil, optparse, codecs
from bisect import bisect_left

VERSION = "0.1"
DESCRIPTION = "repren: Multi-pattern string replacement and file renaming"
NOTES = r'''
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
'''

BACKUP_SUFFIX = ".orig"
DEFAULT_OMIT_PAT = r"\."

def log(source_name, msg):
  if source_name:
    msg = "%s: %s" % (source_name, msg)
  print(msg, file=sys.stderr)

def error(msg):
  print("error: " + msg, file=sys.stderr)
  sys.exit(1)


global tally_files, tally_chars, tally_replacements, tally_files_written, tally_renames
tally_files = 0
tally_chars = 0
tally_replacements = 0
tally_files_written = 0
tally_renames = 0


## String matching

def _overlap(match1, match2):
  return match1.start() < match2.end() and match2.start() < match1.end()

def _sort_drop_overlaps(matches, source_name=None):
  '''Select and sort a set of disjoint intervals, omitting ones that overlap.'''
  non_overlaps = []
  starts = []
  for (match, replacement) in matches:
    index = bisect_left(starts, match.start())
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

def multi_replace(input, patterns, source_name=None):
  '''Replace all occurrences in the input given a list of patterns (regex, replacement), simultaneously, so that no replacement
     affects any other. E.g. { xxx -> yyy, yyy -> xxx } or { xxx -> yyy, y -> z } are possible. If matches overlap, one is
     selected, with matches appearing earlier in the list of patterns preferred.
  '''
  matches = []
  for (regex, replacement) in patterns:
    for match in regex.finditer(input):
      matches.append((match, replacement))
  if len(matches) > 0 and source_name:
    log(source_name, "%s matches" % len(matches))
  new_matches = _sort_drop_overlaps(matches, source_name=source_name)

  global tally_files, tally_chars, tally_replacements
  tally_files += 1
  tally_chars += len(input)
  tally_replacements += len(new_matches)

  return _apply_replacements(input, new_matches)


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

def transform_file(transform, source_path, dest_path, orig_suffix=".orig", temp_suffix=".tmp", dry_run=False):
  '''Transform full contents of file at source_path in memory with specified function, writing dest_path atomically
     and keeping a backup. Source and destination may be the same path.'''
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

        global tally_files_written, tally_renames
        tally_files_written += 1
        if dest_path != source_path:
          tally_renames += 1

def rewrite_file(path, patterns, do_renames=False, do_contents=False, dry_run=False):
   dest_path = multi_replace(path, patterns) if do_renames else path
   transform = None
   if do_contents:
     transform = lambda contents: multi_replace(contents, patterns, source_name=path)
   transform_file(transform, path, dest_path, dry_run=dry_run)

def walk_files(paths, omit_pat=DEFAULT_OMIT_PAT):
  out = []
  omit_re = re.compile(omit_pat)
  for path in paths:
    for (root, dirs, files) in os.walk(path):
      out += [os.path.join(root, f) for f in files if not omit_re.match(f) and not f.endswith(BACKUP_SUFFIX)]
      # Prune subdirectories.
      dirs[:] = [d for d in dirs if not omit_re.match(d)]
  return out

def rewrite_files(root_paths, patterns, do_renames=False, do_contents=False, omit_pat=DEFAULT_OMIT_PAT, dry_run=False):
  log(None, "Using %s pattern(s)" % len(patterns))
  paths = walk_files(root_paths, omit_pat=omit_pat)
  log(None, "Found %s file(s) in %s" % (len(paths), root_paths))
  for path in paths:
    rewrite_file(path, patterns, do_renames=do_renames, do_contents=do_contents, dry_run=dry_run)


## Invocation

def parse_patterns(patterns_str, breakify=True):
  patterns = []
  for line in patterns_str.splitlines():
    try:
      bits = line.split('\t')
      if line.strip().startswith("#"):
        continue
      elif line.strip() and len(bits) == 2:
        (regex, replacement) = bits
        if breakify:
          regex = r'\b' + regex + r'\b'
        patterns.append((re.compile(regex), replacement))
      else:
        error("invalid line in pattern file: %s" % bits)
    except Exception as e:
      error("invalid pattern: %s: %s" % (e, bits))
  return patterns

# Remove excessive epilog formatting in optparse.
optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog

if __name__ == '__main__':
  USAGE = "%prog -p <pattern-file> {-f|-s|-F} [options] [path ...]"
  parser = optparse.OptionParser(usage=USAGE, description=DESCRIPTION, epilog=NOTES, version=VERSION)
  parser.add_option('-f', '--renames', help = 'do file renames (search/replace on full pathnames)', dest = 'do_renames', action = 'store_true')
  parser.add_option('-s', '--contents', help = 'do search/replace on file contents', dest = 'do_contents', action = 'store_true')
  parser.add_option('-F', '--full', help = 'do renames and search/replace', dest = 'do_full', action = 'store_true')
  parser.add_option('-b', '--word-breaks', help = 'require word breaks (regex \\b) on both sides of all matches', dest = 'breakify', action = 'store_true')
  parser.add_option('-p', '--patterns', help = 'file with replacement patterns (see below)', dest = 'patterns')
  parser.add_option('-x', '--exclude', help = 'file/directory name regex to exclude', dest = 'omit_pat', default = DEFAULT_OMIT_PAT)
  parser.add_option('-t', '--parse-only', help = 'parse patterns only', dest = 'parse_only', action = 'store_true')
  parser.add_option('-n', '--dry-run', help = 'dry run: just log matches without changing files', dest = 'dry_run', action = 'store_true')

  (options, root_paths) = parser.parse_args()

  options.do_renames = options.do_renames or options.do_full
  options.do_contents = options.do_contents or options.do_full

  if not options.patterns:
    parser.error('pattern file is required')

  with open(options.patterns, "rb") as f:
    patterns = parse_patterns(f.read(), breakify=options.breakify)

  log(None, "Patterns:\n  " + "\n  ".join(["'%s' -> '%s'" % (regex.pattern, replacement) for (regex, replacement) in patterns]))

  if options.dry_run:
    log(None, "Dry run: no files will be changed")

  if not options.parse_only:
    if len(root_paths) > 0:
      if not options.do_renames and not options.do_contents:
        parser.error('must specify whether to do renames or contents')
      rewrite_files(root_paths, patterns, do_renames=options.do_renames, do_contents=options.do_contents, dry_run=options.dry_run)
    else:
      print(multi_replace(sys.stdin.read(), patterns))

  log(None, "Read %s files (%s chars), found %s replacements, changed %s files (%s renames)" %
      (tally_files, tally_chars, tally_replacements, tally_files_written, tally_renames))

