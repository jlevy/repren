# Shortcut: Clean Up Code

## Instructions

Run full format/typecheck/lint/test cycle and review code following
@shortcut-precommit-process.md.

Create beads for all the following tasks (confirming open tasks for them do not already
exist). Name all tasks with a “Cleanup: ” title to make them easy to spot.
Add a bead for each one and a note to be sure of running all standard tests and fixing
issues.

## Cleanup Tasks

1. **Duplicate types**: Review the code for any types that you have defined and find if
   there are any duplicates and remove or consolidate them.

2. **Duplicate components**: Review the recent changes for duplicate components where we
   can reuse.

3. **Duplicate code**: Review the code base for any duplicate code and refactor it to
   reduce duplication.

4. **Use of any types**: Review types and use actual types over `any`.

   - Don’t create explicit TypeScript interfaces with `any` types—either use proper
     types from your data sources or let TypeScript infer types automatically.

   - Look for interfaces where most/all properties are `any`—delete them and use
     inferred return types or properly type each property from its source.

5. **Use of optional types**: Review types and eliminate as much of optionals as
   possible so we don’t conditionally leak optional state throughout the codebase.

6. **Dead code**: Review the code base for any dead code and remove it.

7. **Remove trivial tests**: Follow @shortcut-cleanup-remove-trivial-tests.md.

8. **Update docstrings**: Follow @shortcut-cleanup-update-docstrings.md.

9. **Consolidate constants and settings**: Determine what files hold shared settings
   (such as `settings.ts` or similar).
   Identify any hard-coded constants in the codebase that are not in these files, and
   add constants or settings as appropriate.

10. **Review function signatures**: Review that parameters to functions are clean and as
    simple as possible. Find any functions/components with parameters that are not
    necessary and remove them.

11. **Avoid optional fields and parameters**: Optional fields on types and optional
    function parameters are error prone as they can be dropped during refactors, leading
    to subtle bugs. Prefer explicit nullable parameters.

12. **Clean up debugging code**: Check for any stray scripts or tests or other code that
    was created in process of debugging that should not be in the production system.
    Remove it.

13. **Review query performance**: Look at all database queries and review.
    Look for and fix:

    - N+1 queries to be more efficient where possible and carefully test any refactors

    - Replace `for` loops with sequential `await` with `Promise.all` for parallel
      execution

    - Batch database queries instead of individual fetches in loops

    - Consolidate nested sequential queries into single `Promise.all` call

14. **Guard early, normalize once** Handle all optional/conditional logic at the top of
    a function. Use early returns for invalid states, or normalize inputs once into a
    guaranteed shape. After that point, code must be straight-line—no repeated
    conditionals.
