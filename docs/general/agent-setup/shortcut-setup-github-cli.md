# GitHub CLI Setup for Agents

## Quick Check

```bash
gh --version && gh auth status
```

If `gh` is available and authenticated, you’re done.

## Installation (if `gh` is missing or blocked)

Install to `~/.local/bin/gh` and add to PATH:

```bash
# Get latest version (with fallback if API fails)
VERSION=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest 2>/dev/null \
  | grep -o '"tag_name": *"v[^"]*"' | head -1 | sed 's/.*"v\([^"]*\)".*/\1/')
VERSION=${VERSION:-2.83.1}

# Download and install
curl -fsSL -o /tmp/gh.tar.gz "https://github.com/cli/cli/releases/download/v${VERSION}/gh_${VERSION}_linux_amd64.tar.gz"
tar -xzf /tmp/gh.tar.gz -C /tmp
mkdir -p ~/.local/bin
cp "/tmp/gh_${VERSION}_linux_amd64/bin/gh" ~/.local/bin/gh
chmod +x ~/.local/bin/gh
rm -rf "/tmp/gh_${VERSION}_linux_amd64" /tmp/gh.tar.gz

# Add to PATH for current session
export PATH="$HOME/.local/bin:$PATH"
```

Verify:

```bash
gh --version
gh auth status
```

## Usage

**Important**: Always specify `-R owner/repo` since git remotes may use a proxy.
(This is needed for example by Claude Code Web.)

```bash
# List PRs
gh pr list -R owner/repo --json number,title,state
# View/update PR
gh pr view 123 -R owner/repo
gh pr comment 123 -R owner/repo --body "Comment text"
# Issues
gh issue list -R owner/repo
gh issue create -R owner/repo --title "Title" --body "Body"
# API (for advanced operations)
gh api repos/owner/repo/pulls/123/comments
```

## Notes

- Authentication must be provided via `GH_TOKEN` environment variable (pre-configured).
  If this is not available, you may suggest the user set this up.

## GitHub Access Token Setup (For User Only)

To set up permissions so agents (like Claude Code Web) may edit GitHub issues and check
workflows using `gh`, create an access token at https://github.com/settings/tokens

- For simplicity: Classic PAT with repo and workflow scope.

- For security: Fine-grained PAT scoped to this repo with Contents + Pull requests
  permissions.

- Typical token scopes recommended for PAT: `repo`, `workflow` (and possibly `read:org`
  to avoid sometimes confusing warnings from `gh`)

Then add env vars to agent setup:
```
GH_TOKEN="github_pat_xxxxx"
GH_PROMPT_DISABLED=1
```
