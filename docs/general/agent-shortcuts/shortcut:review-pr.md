Shortcut: Review PR and Comment

Instructions:

1. Ensure the GitHub CLI `gh` is available and if not use
   @docs/general/agetn-setup/github-cli-setup.md to get it working.

2. Create a temporary PR review doc in /tmp and update it as you go with the next steps.

3. Review the PR provided by the user carefully (If the PR is not clear ask the user).
   Use `gh` to get the PR details and analyze what is new on this branch ahead of
   `origin/main`. Add issues and suggested fixes to the PR review doc as you go.

4. Ensure all docs and relevant specs are in sync, both any specs in the PR and
   `development.md` and any other relevant architecture docs in
   `docs/project/architecture`. If not, add suggested fixes to the PR review doc.

5. Use `gh` GitHub CLI to confirm CI is building correctly just as it did locally.
   Add any issues and suggested fixes to the PR review doc.

6. Give the full review from the PR doc to the user and ask if they’d like you to add as
   a comment on the PR or to begin fixing using beads.
   If they want a comment, use `gh` to add a review comment on the PR with the full PR
   review doc contents and remove the local doc.
   If they want to fix it, carefully create beads for all items in the review.
   Then begin following usual development processes in `development.md` and following
   all coding rules to fix all beads.
   If appropriate, follow @docs/general/agent-guidelines/general-tdd-guidelines.md to
   ensure there are tests for any fixes.
