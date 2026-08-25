## Publishing Releases

This is how to publish a Python package to [**PyPI**](https://pypi.org/) from GitHub
Actions, when using the
[**simple-modern-uv**](https://github.com/jlevy/simple-modern-uv) template.

Thanks to
[the dynamic versioning plugin](https://github.com/ninoseki/uv-dynamic-versioning/) and
the
[`publish.yml` workflow](https://github.com/jlevy/repren/blob/master/.github/workflows/publish.yml),
you can simply create tagged releases (using standard format for the tag name, e.g.
`3.1.0`) on GitHub and the tag will trigger a release build, which then uploads it to
PyPI.

The workflow validates without publishing credentials, then builds from a fresh checkout
containing only the locked build toolchain.
A third job receives only the built distributions and holds the short-lived PyPI OIDC
permission. This separation limits credential exposure; the
[PyPI Trusted Publisher security model](https://docs.pypi.org/trusted-publishers/security-model/)
does not treat it as proof that the source, build dependencies, or distributions are
safe. The validation and build jobs execute repository code, and the final job publishes
their output. Code review, protected release authority, and lockfile review remain the
controls against a malicious or compromised build.

### First-Time Setup

This part is a little confusing the first time.
Here is the simplest way to do it.

**Note:** These steps assume you already have a GitHub repo with your code pushed.
If not, create an **empty** GitHub repo (no README, no .gitignore, no license; the
template already provides these) and push your code to it.
See the
[README](https://github.com/jlevy/simple-modern-uv#option-2-use-copier-and-git-yourself)
for details.

1. **Get a PyPI account** at [pypi.org](https://pypi.org/) and sign in.

2. **Pick a name for the project** that isn’t already taken.

   - Repren’s package page is <https://pypi.org/project/repren/>.

   - If needed, update your `pyproject.toml` with the correct name.

3. **Authorize** your repository to publish to PyPI:

   - In the GitHub repository, go to **Settings → Environments** and create a
     [GitHub environment](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
     named `pypi`. No secret is stored there.
     Entering the same name in PyPI restricts this Trusted Publisher to jobs that
     declare the environment.

   - Repren has a solo maintainer, so a mandatory second approval would block releases.
     The release-only trigger removes the ordinary manual-branch path, but anyone
     allowed to create a matching release tag may still invoke it.
     If repository writers who should not publish are added, use a GitHub tag ruleset to
     restrict creation and updates of version tags to release maintainers, and/or
     require an environment reviewer.
     Limiting the environment to selected release tags rejects other refs but does not
     control who can create a matching tag.

   - Go to [the publishing settings page](https://pypi.org/manage/account/publishing/).

   - Find “Trusted Publisher Management” and register your GitHub repo as a new
     “pending” trusted publisher.

   - Enter `repren` as the project, `jlevy` as the owner, `repren` as the repository,
     `publish.yml` as the workflow name, and `pypi` as the environment.

     If Repren’s existing Trusted Publisher still has a blank environment, it remains
     compatible but unconstrained.
     Update it to `pypi` in the project’s PyPI publishing settings to obtain the
     environment restriction.

4. **Create a release** on GitHub:

   - Commit code and make sure it’s running correctly.

   - Go to your GitHub project page, then click on Actions tab.

   - Confirm all tests are passing in the last CI workflow.
     (If you want, you can even publish this template when it’s empty as just a stub
     project, to try all this out.)

   - Go to your GitHub project page, click on Releases.

   - Fill in the tag and the release name.
     Select to create a new tag, and pick a version.
     Repren uses an unprefixed semantic version such as `3.1.0`, matching
     `pattern = "default-unprefixed"` in `pyproject.toml`.

   - Submit to create the release.

5. **Confirm it publishes to PyPI**

   - Watch for the release workflow in the GitHub Actions tab.

   - If it succeeds, it appears at <https://pypi.org/project/repren/>.

### Publishing Subsequent Releases

Follow this checklist for each new release.

#### Pre-Release Checklist

1. **Cut the release from an up-to-date `master`:**

   ```shell
   git checkout master
   git pull origin master
   git status  # confirm a clean working tree
   ```

2. **Verify all changes are committed and pushed:**

   ```shell
   git log origin/master..HEAD  # should be empty if pushed
   ```

3. **Run linting and tests locally:**

   ```shell
   make
   make lint-check
   make format-check
   make gendocs-check
   make build
   ```

4. **Confirm CI is passing on `master`:**

   ```shell
   gh run list --branch master --limit 3
   ```

   Or check the Actions tab on GitHub.
   The most recent run for the commit you’re about to tag must be green (a superseded
   older failure is fine).

5. **Determine the new version number:**

   ```shell
   # Check current/latest version:
   gh release list --limit 1
   ```

   Use [semantic versioning](https://semver.org/):

   - **Patch** (e.g., `3.1.0` → `3.1.1`): Bug fixes, minor changes

   - **Minor** (e.g., `3.1.1` → `3.2.0`): New features, backward-compatible

   - **Major** (e.g., `3.2.0` → `4.0.0`): Breaking changes

#### Create the Release

6. **Review changes since the last release:**

   ```shell
   # Get the last release tag:
   LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')

   # View commits since last release:
   git log ${LAST_TAG}..HEAD --oneline

   # View full diff:
   git diff ${LAST_TAG}..HEAD
   ```

7. **Write the release notes in a file, then create the release:**

   Author the notes as plain Markdown in a file (see
   [Release Notes Format](#release-notes-format) below), then pass it with
   `--notes-file`. Writing the notes in a file keeps the shell out of the way: release
   notes routinely contain backticks and `$`, which a shell heredoc would try to run as
   commands or expand as variables.
   End the notes with a *concrete* compare link built from the actual tags (substitute
   the real `LAST_TAG` and `NEW_TAG` values into the URL), e.g.
   `https://github.com/jlevy/repren/compare/3.1.0...3.1.1`.

   ```shell
   NEW_TAG="X.Y.Z"  # Replace with the actual unprefixed version

   # Edit release-notes.md in your editor, ending with the concrete compare link.

   gh release create "${NEW_TAG}" --title "${NEW_TAG}" --notes-file release-notes.md
   ```

   Alternatively, use `--generate-notes` for GitHub’s auto-generated notes.

8. **Verify the release published successfully:**

   ```shell
   # Check the release workflow:
   gh run list --workflow=publish.yml --limit 1

   # Verify on PyPI (may take a minute):
   # https://pypi.org/project/repren
   ```

   Once it appears on PyPI, smoke-test that the published artifact actually resolves and
   installs from PyPI. If your project exposes a CLI:

   ```shell
   uvx --from repren==X.Y.Z repren --version
   ```

### Release Notes Format

Use this structure for release notes:

```markdown
## What's Changed

### Bug Fixes

**Short title of fix**

Description of what was fixed and why it matters.

### New Features

**Short title of feature**

Description of the new capability.

### Breaking Changes

**Short title of breaking change**

Description of what changed and how to migrate.

### Full Changelog

https://github.com/jlevy/repren/compare/PREVIOUS...NEW
```

Guidelines:

- Use `## What's Changed` as the top-level heading.

- Group changes under `### Bug Fixes`, `### New Features`, `### Breaking Changes`, etc.
  as appropriate.

- Use `**bold**` for short titles of individual changes.

- Include technical details only when helpful for users.

- Always include the Full Changelog compare link at the end.

- For small releases, a simple bullet list is acceptable instead of full sections.

* * *

*This file was built with
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
