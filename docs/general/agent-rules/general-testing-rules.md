---
description: General Testing Rules
globs:
alwaysApply: true
---
## General Testing Rules

- Write the minimal set of tests with the maximal coverage.
  Write as few tests as possible that *also* cover the desired functionality.
  If you see many similar tests, review to see if any can be removed or rewritten to be
  shorter without reducing test coverage.

- Do NOT write unit tests that are obviously going to pass (like creating objects and
  validating they are set on an object).
  These needlessly clutter the codebase.
  For example:

  - Do not write a test that simply instantiates a class and the object’s fields are
    set.

- Do NOT write a test that is trivial enough it is obviously tested as part of another
  test in the same codebase.

- Don’t test implementation details: Focus on behavior and outcomes, not internal
  mechanics, so tests remain valid when you refactor.

- Test edge cases and boundaries: Include tests for empty inputs, nulls, maximums,
  minimums, and error conditions—not just happy paths.
