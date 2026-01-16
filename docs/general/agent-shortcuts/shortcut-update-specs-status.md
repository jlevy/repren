Shortcut: Update Specs Progress

Instructions:

Create a to-do list with the following items then perform all of them:

1. Make a list of all active specs in @docs/project/specs/active/*.md

2. For each distinct effort, check there is an *spec bead* (that is, an umbrella bead
   that covers the whole spec), for it.
   If there is not, create one.
   Always put “Spec: ” as a prefix on the top-level spec bead title.
   Add sub-beads as dependencies if they don’t exist (such as for each phase of a
   multi-phase spec) but do not use a “Spec: ” prefix on sub-beads.

3. Then for each bead update its status to reflect the actual current work completed, if
   any. Review the specs and the code.
   If it’s unclear, use GitHub CLI if necessary to review commits and PRs.
   Then update the beads.

4. For each spec that is complete, move it from @docs/project/specs/active to
   @docs/project/specs/done

5. Do a bead sync to make sure all bead changes are synced with the repo.
