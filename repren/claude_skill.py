"""
Claude Code skill installation for repren.

This module provides functionality to install the repren skill for Claude Code,
making it available either globally across all projects or within a specific project.
"""

import sys
from pathlib import Path
from typing import Literal


def get_skill_content() -> str:
    """Read SKILL.md from package data.

    Returns:
        The content of the SKILL.md file as a string.

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


def install_skill(
    scope: Literal["global", "project"] | None = None, interactive: bool = True
) -> None:
    """Install repren skill for Claude Code.

    Args:
        scope: Where to install the skill:
            - 'global': ~/.claude/skills/repren (available everywhere)
            - 'project': .claude/skills/repren (current project only)
            - None: Ask user interactively (if interactive=True) or default to 'global'
        interactive: Whether to prompt user for choices. If False, uses defaults.

    The skill will be installed as SKILL.md in the appropriate directory,
    making it automatically available to Claude Code.
    """
    # Determine installation scope
    if scope is None and interactive:
        print("\n" + "=" * 70)
        print("Install repren skill for Claude Code")
        print("=" * 70)
        print("\nWhere should the skill be installed?\n")
        print("  [1] Global (~/.claude/skills)")
        print("      Available in all projects (recommended)")
        print()
        print("  [2] Project (.claude/skills)")
        print("      Current project only, can be committed for team")
        print()

        try:
            choice = input("Choose [1]: ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            print("\n\nCancelled.")
            sys.exit(0)

        scope = "global" if choice == "1" else "project"
    elif scope is None:
        # Non-interactive default
        scope = "global"

    # Determine installation directory
    if scope == "global":
        skill_dir = Path.home() / ".claude" / "skills" / "repren"
        location_desc = "globally"
        location_path = "~/.claude/skills/repren"
    else:  # scope == 'project'
        skill_dir = Path.cwd() / ".claude" / "skills" / "repren"
        location_desc = "in current project"
        location_path = ".claude/skills/repren"

    # Load skill content from package data
    try:
        skill_content = get_skill_content()
    except (ImportError, FileNotFoundError) as e:
        print(f"\n✗ Error: Could not load skill content: {e}", file=sys.stderr)
        print("\nThis command requires repren to be installed as a package.", file=sys.stderr)
        print("Install with: uv tool install repren", file=sys.stderr)
        sys.exit(1)

    # Create directory and install
    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"

        skill_file.write_text(skill_content, encoding="utf-8")

        print("\n" + "=" * 70)
        print(f"✓ Repren skill installed {location_desc}")
        print("=" * 70)
        print(f"\nLocation: {skill_file}")
        print(f"          ({location_path})")
        print("\nClaude Code will now automatically use repren for refactoring tasks.")

        if scope == "project":
            print("\n" + "-" * 70)
            print("Tip: Commit .claude/skills/ to share this skill with your team.")
            print("-" * 70)

        print()  # Blank line for clean output

    except PermissionError as e:
        print(f"\n✗ Permission denied: {e}", file=sys.stderr)
        print(f"\nCould not write to {skill_dir}", file=sys.stderr)
        print("Check directory permissions and try again.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"\n✗ Installation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Command-line interface for skill installation.

    Can be run directly for testing:
        python -m repren.claude_skill --global
        python -m repren.claude_skill --project
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Install repren Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode (asks where to install)
  %(prog)s --global           # Install globally (~/.claude/skills)
  %(prog)s --project          # Install in current project (.claude/skills)
  %(prog)s --global --quiet   # Non-interactive global install
        """,
    )

    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument(
        "--global",
        dest="scope",
        action="store_const",
        const="global",
        help="Install globally (~/.claude/skills) - available everywhere",
    )
    scope_group.add_argument(
        "--project",
        dest="scope",
        action="store_const",
        const="project",
        help="Install in current project (.claude/skills) - shareable via git",
    )

    parser.add_argument(
        "--quiet",
        dest="interactive",
        action="store_false",
        help="Non-interactive mode (use defaults, no prompts)",
    )

    args = parser.parse_args()

    install_skill(scope=args.scope, interactive=args.interactive)


if __name__ == "__main__":
    main()
