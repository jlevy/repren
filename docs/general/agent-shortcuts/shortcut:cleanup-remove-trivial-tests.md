# Shortcut: Remove Trivial Tests

## Instructions

Review the codebase for trivial tests that do not add meaningful coverage and remove
them.

## What Constitutes a Trivial Test

A test is trivial and should be removed if it:

1. **Tests object construction**: Simply instantiates a class/object and validates that
   fields are set to the values they were given.

2. **Tests obvious pass cases**: Creates objects and validates they match what was set,
   such as `expect(obj.name).toBe('test')` right after `const obj = { name: 'test' }`.

3. **Duplicates coverage**: Tests something that is already tested as part of another
   test in the same codebase.

4. **Tests implementation details**: Tests specific internal mechanics rather than
   behavior and outcomes in ways that are brittle to refactoring.

5. **Tests declared values**: Validates that a constant or declared value matches what
   it was set to.

## What to Preserve

Keep tests that:

- Test edge cases and boundaries (empty inputs, nulls, maximums, minimums, error
  conditions)

- Cover meaningful behavior and outcomes

- Add unique coverage not provided by other tests

- Test integration between components

- Verify error handling and failure modes

## Process

1. Review @docs/general/agent-rules/general-testing-rules.md for context

2. Scan all test files in the codebase

3. Identify tests matching the trivial patterns above

4. Remove trivial tests while preserving meaningful coverage

5. Run the full test suite to ensure no regressions
