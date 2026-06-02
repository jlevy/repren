"""
Agent skill installation for repren.

This module installs the repren skill for coding agents. The skill is written to
both the portable cross-agent location (`.agents/skills/repren/`) and the Claude Code
mirror (`.claude/skills/repren/`).

repren is a general-purpose utility with no per-project configuration, so it is a
dual-scope skill: it can be installed into a single project or globally for the user.
Scope is resolved `git config`-style: implicit when unambiguous, a hard error when not
(see `resolve_install_target`).

The skill invokes repren through ``uvx repren@latest``. repren has zero runtime
dependencies, so the only code a runner ever fetches is repren itself; for an extra
safety margin, opt into uv's release cool-off (``UV_EXCLUDE_NEWER``) in your environment.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# Surfaces the skill is written to, beneath the resolved install root.
SKILL_SURFACES: list[tuple[str, str]] = [
    ("portable", ".agents"),  # cross-agent: Codex, Gemini CLI, pi, others
    ("claude", ".claude"),  # Claude Code mirror
]


class SkillScopeError(Exception):
    """Raised when the skill install scope cannot be resolved unambiguously."""


def get_skill_content() -> str:
    """Read SKILL.md from package data.

    Returns:
        The SKILL.md content.

    Raises:
        ImportError: If package resources cannot be accessed.
        FileNotFoundError: If SKILL.md cannot be found in package data.
    """
    try:
        # Python 3.9+ importlib.resources API
        from importlib.resources import files

        skill_file = files("repren").joinpath("skills/SKILL.md")
        return skill_file.read_text(encoding="utf-8")
    except (ImportError, AttributeError):
        # Fallback for older Python versions
        try:
            import pkg_resources  # type: ignore[import-not-found]  # pyright: ignore[reportMissingImports]

            return pkg_resources.resource_string("repren", "skills/SKILL.md").decode("utf-8")
        except Exception as e:
            raise ImportError(
                f"Could not load skill from package data: {e}\n"
                "Ensure repren is installed as a package, not run as a standalone script."
            ) from e


@dataclass
class InstallTarget:
    """A resolved skill install location.

    Attributes:
        root: The directory the skill surfaces are written beneath.
        mode: Either ``"project"`` or ``"global"``.
    """

    root: Path
    mode: str


def _git_root(path: Path) -> Path | None:
    """Return the repository root for ``path`` (nearest ancestor with a ``.git``), or None.

    ``.git`` is matched whether it is a directory (normal clone) or a file (worktree or
    submodule gitlink), so installs land at the repo root rather than the subdirectory the
    command happened to run from.
    """
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _in_git_repo(path: Path) -> bool:
    """Return True if ``path`` is inside a git repository (a ``.git`` exists at or above)."""
    return _git_root(path) is not None


def resolve_install_target(
    *,
    project: bool = False,
    global_install: bool = False,
    dir: str | None = None,
    no_repo_check: bool = False,
    cwd: Path | None = None,
    home: Path | None = None,
) -> InstallTarget:
    """Resolve where to install the skill, copying the ``git config`` scope model.

    Scope is implicit when unambiguous and a hard error when not, so that
    ``cd ~ && repren --install-skill`` never silently rewrites the user's global agent
    surfaces.

    Args:
        project: Force a project-local install.
        global_install: Force a user-global install under ``$HOME``.
        dir: Explicit project root (implies project mode); mutually exclusive with
            ``global_install``.
        no_repo_check: Allow a project install when ``cwd`` is not inside a git repo.
        cwd: Override the current directory (for testing).
        home: Override the home directory (for testing).

    Returns:
        The resolved :class:`InstallTarget`.

    Raises:
        SkillScopeError: If the scope is ambiguous or the request is contradictory.
    """
    cwd = (cwd or Path.cwd()).resolve()
    home = (home or Path.home()).resolve()

    if project and global_install:
        raise SkillScopeError("--project and --global are mutually exclusive.")
    if global_install and dir is not None:
        raise SkillScopeError("--global and --dir are mutually exclusive.")

    # Resolve the scope mode.
    if global_install:
        mode = "global"
    elif project or dir is not None:
        mode = "project"
    else:
        # Implicit scope (the git config rule): resolve before writing anything.
        if cwd == home or cwd == Path(cwd.anchor):
            raise SkillScopeError(f"ambiguous install scope in {cwd}: pass --project or --global.")
        if _in_git_repo(cwd):
            mode = "project"
        else:
            raise SkillScopeError(
                f"{cwd} is not inside a git repository: pass "
                "--project --no-repo-check to install here anyway, or --global."
            )

    if mode == "global":
        return InstallTarget(root=home, mode="global")

    # Project mode. An explicit --dir wins as given; otherwise install at the repository
    # root (not the subdirectory the command ran from), so `repren --install-skill` from
    # `repo/subdir` writes to `repo/`, matching the documented project-local behavior.
    if dir is not None:
        root = Path(dir).resolve()
    else:
        root = _git_root(cwd) or cwd
    if root == home:
        # --project --dir ~ is always refused; that is exactly what --global is for.
        raise SkillScopeError(
            f"--project: refusing to install into {root} (home directory). "
            "That would write to your global agent surfaces. Use --global instead."
        )
    if dir is None and not no_repo_check and not _in_git_repo(root):
        raise SkillScopeError(
            f"--project: {root} is not inside a git repository. "
            "Pass --no-repo-check to install here anyway, or --global."
        )
    return InstallTarget(root=root, mode="project")


def install_skill(
    *,
    project: bool = False,
    global_install: bool = False,
    dir: str | None = None,
    no_repo_check: bool = False,
) -> None:
    """Resolve the install scope and write the repren skill to both surfaces.

    Writes the skill under the resolved root:

    - ``<root>/.agents/skills/repren/SKILL.md`` (portable: Codex, Gemini, pi, others)
    - ``<root>/.claude/skills/repren/SKILL.md`` (Claude Code)

    Args:
        project: Force a project-local install.
        global_install: Force a user-global install under ``$HOME``.
        dir: Explicit project root (implies project mode).
        no_repo_check: Allow a project install outside a git repository.

    Raises:
        SkillScopeError: If the scope cannot be resolved unambiguously.
    """
    target = resolve_install_target(
        project=project,
        global_install=global_install,
        dir=dir,
        no_repo_check=no_repo_check,
    )

    # Load and render skill content from package data.
    try:
        skill_content = get_skill_content()
    except (ImportError, FileNotFoundError) as e:
        print(f"\n✗ Error: Could not load skill content: {e}", file=sys.stderr)
        print("\nThis command requires repren to be installed as a package.", file=sys.stderr)
        print("Install with: uv tool install repren", file=sys.stderr)
        sys.exit(1)

    surface_names = ", ".join(name for name, _ in SKILL_SURFACES)
    targets = [
        (name, target.root / parent / "skills" / "repren" / "SKILL.md")
        for name, parent in SKILL_SURFACES
    ]

    # Print the resolved target before writing, so the user can ctrl-c if it is wrong.
    print(f"\nInstalling repren skill ({target.mode} mode) into: {target.root}")
    print(f"  surfaces: {surface_names}")

    try:
        written: list[Path] = []
        for _name, skill_file in targets:
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(skill_content, encoding="utf-8")
            written.append(skill_file)

        print("\n" + "=" * 70)
        print(f"✓ Repren skill installed ({target.mode} mode)")
        print("=" * 70)
        print("\nLocations:")
        for skill_file in written:
            print(f"  {skill_file}")
        print("\nCoding agents will now use repren for refactoring tasks.")
        print("To uninstall, remove the repren/ directories above.")

        if target.mode == "project":
            print("\n" + "-" * 70)
            print("Tip: Commit .agents/skills/ and .claude/skills/ to share this with your team.")
            print("-" * 70)

        print()  # Blank line for clean output

    except PermissionError as e:
        print(f"\n✗ Permission denied: {e}", file=sys.stderr)
        print(f"\nCould not write under {target.root}", file=sys.stderr)
        print("Check directory permissions and try again.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"\n✗ Installation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Command-line interface for skill installation.

    Can be run directly for testing:
        python -m repren.agent_skill --project
        python -m repren.agent_skill --global
        python -m repren.agent_skill --project --dir /path/to/repo
    """
    parser = argparse.ArgumentParser(
        description="Install repren agent skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scope is resolved like `git config`: implicit when unambiguous, an error when not.

Examples:
  %(prog)s --project              # Install into the current project
  %(prog)s --global               # Install globally (under ~)
  %(prog)s --project --dir REPO   # Install into a specific project root
        """,
    )

    parser.add_argument("--project", action="store_true", help="install into the current project")
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="install globally under ~",
    )
    parser.add_argument("--dir", metavar="DIR", help="explicit project root (implies --project)")
    parser.add_argument(
        "--no-repo-check",
        dest="no_repo_check",
        action="store_true",
        help="allow --project outside a git repository",
    )

    args = parser.parse_args()

    try:
        install_skill(
            project=args.project,
            global_install=args.global_install,
            dir=args.dir,
            no_repo_check=args.no_repo_check,
        )
    except SkillScopeError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
