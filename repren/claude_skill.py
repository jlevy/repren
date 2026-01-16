"""
Claude Code skill installation for repren.

This module provides functionality to install the repren skill for Claude Code,
making it available either globally across all projects or within a specific project.
"""

import sys
from pathlib import Path


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


def install_skill(install_dir: str | None = None) -> None:
    """Install repren skill for Claude Code.

    Args:
        install_dir: Base directory for installation. The skill will be installed to
            {install_dir}/.claude/skills/repren/SKILL.md
            - None (default): Install to home directory (~/.claude/skills/repren)
            - '.': Install to current directory (./.claude/skills/repren)
            - Any path: Install to that path

    The skill will be installed as SKILL.md in the appropriate directory,
    making it automatically available to Claude Code.
    """
    # Determine installation directory
    if install_dir is None:
        # Default: global install to home directory
        base_dir = Path.home()
        location_desc = "globally"
        location_path = "~/.claude/skills/repren"
    else:
        # User-specified directory
        base_dir = Path(install_dir).resolve()
        location_desc = f"to {base_dir}"
        location_path = str(base_dir / ".claude" / "skills" / "repren")

    skill_dir = base_dir / ".claude" / "skills" / "repren"

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
        print(f"To uninstall, remove this directory: {skill_dir}")

        # Show tip for project installs
        if install_dir is not None:
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
        python -m repren.claude_skill
        python -m repren.claude_skill --claude-dir .
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Install repren Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Install globally (~/.claude/skills)
  %(prog)s --claude-dir .     # Install in current directory (./.claude/skills)
  %(prog)s --claude-dir /path # Install to /path/.claude/skills
        """,
    )

    parser.add_argument(
        "--claude-dir",
        dest="install_dir",
        metavar="DIR",
        help="directory for .claude/skills/repren (defaults to home directory)",
    )

    args = parser.parse_args()

    install_skill(install_dir=args.install_dir)


if __name__ == "__main__":
    main()
