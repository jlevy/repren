## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking.
Do NOT use markdown TODOs or other ad-hoc issue tracking methods.

**Check if bd is installed and get workflow context:**

```bash
if command -v bd &>/dev/null; then
  bd prime
else
  echo "bd not installed - run installation below"
fi
```

If bd is already installed, `bd prime` loads the workflow context.
**Skip to the “Workflow for AI Agents” section below.**

**If bd is not installed**, use the direct download method:

```bash
# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
[ "$ARCH" = "x86_64" ] && ARCH="amd64"
[ "$ARCH" = "aarch64" ] && ARCH="arm64"

# Get latest version from GitHub API
BD_VERSION=$(curl -sI https://github.com/steveyegge/beads/releases/latest | \
  grep -i "^location:" | sed 's/.*tag\///' | tr -d '\r\n')

# Download and install the binary
curl -fsSL -o /tmp/beads.tar.gz \
  "https://github.com/steveyegge/beads/releases/download/${BD_VERSION}/beads_${BD_VERSION#v}_${OS}_${ARCH}.tar.gz"
tar -xzf /tmp/beads.tar.gz -C /tmp
mkdir -p ~/.local/bin
cp /tmp/bd ~/.local/bin/
chmod +x ~/.local/bin/bd
export PATH="$HOME/.local/bin:$PATH"
bd prime   # Get workflow context
```

For troubleshooting, see: https://github.com/steveyegge/beads/releases

**If bd says `Error: no beads database found`:**
```bash
bd init
bd prime
```

**If you encounter other errors:**
```bash
bd doctor       # Check installation health
bd doctor --fix # Fix any setup issues
```

### Sync Branch Configuration

Beads can commit issue changes to a dedicated sync branch (recommended for team
projects). This uses git worktrees internally.

**IMPORTANT:** Never use `main` as the sync branch - it locks `main` in a worktree,
preventing normal `git checkout main`. Use a dedicated branch like `beads-sync`.

**Check current config:**
```bash
bd config get sync.branch
```

**For new projects** - add to `.beads/config.yaml`:
```yaml
sync-branch: 'beads-sync'
```

**For existing projects with wrong sync branch:**
```bash
bd config set sync.branch beads-sync
bd daemon stop && bd daemon start
```

**If you see “fatal: ‘main’ is already used by worktree”:**
```bash
# Fix: remove beads worktrees and change sync branch
rm -rf .git/beads-worktrees .git/worktrees/beads-*
git worktree prune
bd config set sync.branch beads-sync
bd daemon stop && bd daemon start
```

### Git Merge Driver (required for each clone)

The `.gitattributes` file configures beads JSONL files to use a custom merge driver, but
the driver must be registered in your local git config:

```bash
git config merge.beads.driver "bd merge %A %O %A %B"
git config merge.beads.name "bd JSONL merge driver"
```

Verify with: `bd doctor | grep "Git Merge Driver"` (should show checkmark)

### SQLite WAL Mode Errors (common in containers/VMs)

If you see `failed to enable WAL mode: sqlite3: locking protocol`, use JSONL-only mode:

```bash
echo "no-db: true" >> .beads/config.yaml
# Or use --no-db flag: bd --no-db status
```

### Issue Types

- `bug` - Something broken

- `feature` - New functionality

- `task` - Work item (tests, docs, refactoring)

- `epic` - Large feature with subtasks

- `chore` - Maintenance (dependencies, tooling)

- `merge-request` - Code review / merge request

### Priorities

Use `0-4` or `P0-P4` format (NOT "high"/"medium"/"low"):

- `0` / `P0` - Critical (security, data loss, broken builds)

- `1` / `P1` - High (major features, important bugs)

- `2` / `P2` - Medium (default, nice-to-have)

- `3` / `P3` - Low (polish, optimization)

- `4` / `P4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues

2. **Claim your task**: `bd update <id> --status in_progress`

3. **Work on it**: Implement, test, document

4. **Discover new work?** Create linked issue:

   - `bd create "Found bug" -p 1 --deps "discovered-from:<parent-id>"`

   - Dependencies format: `'type:id'` or `'id'` (e.g.,
     `'discovered-from:bd-20,blocks:bd-15'`)

5. **Complete**: `bd close <id>` or close multiple at once: `bd close <id1> <id2> ...`

6. **Session close protocol** (CRITICAL - before saying “done”):
   ```bash
   git status              # Check what changed
   git add <files>         # Stage code changes
   bd sync --from-main     # Pull beads updates from main
   git commit -m "..."     # Commit code changes
   ```

### Useful Commands

- `bd ready` - Show issues ready to work (no blockers)

- `bd blocked` - Show blocked issues

- `bd show <id>` - Detailed issue view with dependencies

- `bd doctor` - Check and fix beads installation health

- `bd quickstart` - Quick start guide

- `bd prime` - Get workflow context (auto-called by hooks)

- `bd <command> --help` - See all flags for any command

### Important Rules

- Use bd for ALL task tracking

- Always use `--json` flag for programmatic use

- Link discovered work with `discovered-from` dependencies

- Check `bd ready` before asking “what should I work on?”

- Store AI planning docs in `history/` directory

- Run `bd sync --from-main` at session end

- Do NOT use "high"/"medium"/"low" for priorities (use 0-4 or P0-P4)

- Do NOT use external issue trackers

- Do NOT use `main` as the sync branch (use `beads-sync`)
