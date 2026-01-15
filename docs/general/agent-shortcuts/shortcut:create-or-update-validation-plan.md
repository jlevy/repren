Shortcut: Create or Update Validation Plan

Instructions:

Create a to-do list with the following items then perform all of them:

1. **Confirm the relevant spec docs:** Check if a Plan Spec and/or Implementation Spec
   are in scope or provided by the user.
   You should find them in @docs/project/specs/active/ with plan- and impl- prefixes
   (e.g., plan-YYYY-MM-DD-*.md and impl-YYYY-MM-DD-*.md).
   If isn’t clear, stop and ask!

2. **Find or create a new Validation Plan doc:** Check if there is a Validation Plan
   already present for this work.
   It should be in @docs/project/specs/active/valid-YYYY-MM-DD-some-description.md (with
   the same description in the filename as the other specs).
   If not, Copy @docs/project/specs/template-validation-spec.md to
   @docs/project/specs/active/valid-YYYY-MM-DD-feature-some-description.md (filling in
   the date and the appropriate description of the feature, matching the Plan Spec
   filename stem with valid- replacing plan-). Fill in the template, in particular
   covering everything you have validated via autoamted tests and in a separate section
   everything the user should validate.
   Don’t repeat things for manual validation if they are fully validated by automated
   tests like unit or integration tests.
   Add an “Open Questions” section with clarifications requested from the user if scope
   of validation is unclear.

3. **Update Validation Plan doc:** Fill in or review and update the validation plan,
   ensuring it makes sense, completely summarizes automated testing, testing you have
   done, and manual testig for the user.
   Ensure it is in sync with all code and beads.
   In particular cover everything you have validated via automated tests and in a
   separate section everything the user should validate.
   Don’t repeat things for manual validation if they are fully validated by automated
   tests like unit or integration tests.
   Add an “Open Questions” section with clarifications requested from the user if scope
   of validation is unclear.

4. **Commit the Validation Plan:** Commit your updated the plan.
