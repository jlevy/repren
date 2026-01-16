Shortcut: Review and Fix PR Using Beads

Instructions:

1. Ensure the GitHub CLI `gh` is available and if not use
   @docs/general/agetn-setup/github-cli-setup.md to get it working.

2. Review the PR provided by the user carefully (If the PR is not clear ask the user).
   Use `gh` to get the PR details and analyze what is new on this branch ahead of
   `origin/main`. Create a bead for this and add sub-beads as you go for any issues that
   need to be addressed so all are tracked.
   Include the PR for context on each.

3. Ensure all docs and relevant specs are in sync, both any specs in the PR and
   `development.md` and any other relevant architecture docs in
   `docs/project/architecture`. If not, carefully add more beads with full context so
   other agents or you can make the required updates and corrections.

4. Check you are on the correct branch to match the PR. (If not ask the user what to
   do.) Fix all beads, following usual development processes in `development.md` and
   following all coding rules.
   If appropriate, follow @docs/general/agent-guidelines/general-tdd-guidelines.md to
   ensure there are tests for any fixes.

5. Use `gh` GitHub CLI to confirm CI is building correctly just as it did locally.
   Fix any remaining issues.

6. Use `gh` to Update the PR description if necessary to be current and include all
   testing and any manual validation still needed.
