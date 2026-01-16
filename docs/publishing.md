## Publishing Releases

This is how to publish a Python package to [**PyPI**](https://pypi.org/) from GitHub
Actions, when using the
[**simple-modern-uv**](https://github.com/jlevy/simple-modern-uv) template.

Thanks to
[the dynamic versioning plugin](https://github.com/ninoseki/uv-dynamic-versioning/) and
the
[`publish.yml` workflow](https://github.com/jlevy/repren/blob/master/.github/workflows/publish.yml),
you can simply create tagged releases (using the tag name format matching your version,
e.g. `1.0.2`) on GitHub and the tag will trigger a release build, which then uploads it
to PyPI.

### First-Time Setup

This part is a little confusing the first time.
Here is the simplest way to do it.

1. **Get a PyPI account** at [pypi.org](https://pypi.org/) and sign in.

2. **Pick a name for the project** that isn’t already taken.

   - Go to `https://pypi.org/project/PROJECT` to see if another project with that name
     already exits.

   - If needed, update your `pyproject.toml` with the correct name.

3. **Authorize** your repository to publish to PyPI:

   - Go to [the publishing settings page](https://pypi.org/manage/account/publishing/).

   - Find “Trusted Publisher Management” and register your GitHub repo as a new
     “pending” trusted publisher.

   - Enter the project name, repo owner, repo name, and `publish.yml` as the workflow
     name. (You can leave the “environment name” field blank.)

4. **Create a release** on GitHub:

   - Commit code and make sure it’s running correctly.

   - Go to your GitHub project page, then click on Actions tab.

   - Confirm all tests are passing in the last CI workflow.
     (If you want, you can even publish this template when it’s empty as just a stub
     project, to try all this out.)

   - Go to your GitHub project page, click on Releases.

   - Fill in the tag and the release name.
     Select to create a new tag, and pick a version.
     A good option is `0.1.0` (matching `pattern = "default-unprefixed"` in
     pyproject.toml).

   - Submit to create the release.

5. **Confirm it publishes to PyPI**

   - Watch for the release workflow in the GitHub Actions tab.

   - If it succeeds, you should see it appear at `https://pypi.org/project/repren`.

### Publishing Subsequent Releases

Follow this checklist for each new release.

#### Pre-Release Checklist

1. **Verify all changes are committed and pushed:**

   ```shell
   git status
   git log origin/master..HEAD  # should be empty if pushed
   ```

2. **Run linting and tests locally:**

   ```shell
   make lint
   make test
   ./tests/run.sh  # integration tests
   ```

3. **Confirm CI is passing:**

   ```shell
   gh run list --limit 3
   ```

   Or check the Actions tab on GitHub.

4. **Determine the new version number:**

   ```shell
   # Check current/latest version:
   gh release list --limit 1
   ```

   Use [semantic versioning](https://semver.org/):

   - **Patch** (e.g., `1.0.1` → `1.0.2`): Bug fixes, minor changes

   - **Minor** (e.g., `1.0.2` → `1.1.0`): New features, backward-compatible

   - **Major** (e.g., `1.1.0` → `2.0.0`): Breaking changes

#### Create the Release

5. **Generate release notes content:**

   Review changes since the last release:

   ```shell
   # Get the last release tag:
   LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')
   
   # View commits since last release:
   git log ${LAST_TAG}..HEAD --oneline
   
   # View full diff:
   git diff ${LAST_TAG}..HEAD
   ```

6. **Create the release with `gh`:**

   ```shell
   NEW_TAG="X.Y.Z"  # Replace with actual version (unprefixed)
   LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')
   
   gh release create "${NEW_TAG}" \
     --title "${NEW_TAG}" \
     --notes "$(cat <<'EOF'
   ## What's Changed
   
   [Summarize changes here--see format guide below]
   
   ### Full Changelog
   
   https://github.com/jlevy/repren/compare/${LAST_TAG}...${NEW_TAG}
   EOF
   )"
   ```

   Alternatively, use `--generate-notes` for GitHub’s auto-generated notes, or
   `--notes-file FILENAME` to read from a file.

7. **Verify the release published successfully:**

   ```shell
   # Check the release workflow:
   gh run list --workflow=publish.yml --limit 1
   
   # Verify on PyPI (may take a minute):
   # https://pypi.org/project/repren
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

*This project uses [simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
