"""
Agent skill installation for repren.

This module installs the repren skill for coding agents. The skill is written to
both the portable cross-agent location (`.agents/skills/repren/`) and the Claude Code
mirror (`.claude/skills/repren/`), either globally (under ``$HOME``) or within a
specific project.

The skill text in ``skills/SKILL.md`` is a template: the ``{{REPREN_VERSION}}``
placeholder is replaced with the installed repren version so the skill's pinned
zero-install fallback (``uvx repren@<version>``) always matches what produced it.
"""

import sys
from pathlib import Path

# Placeholder in skills/SKILL.md replaced with the installed repren version at render time.
VERSION_PLACEHOLDER = "{{REPREN_VERSION}}"


def _pinned_version() -> str:
    """Return the installed repren version suitable for a ``uvx repren@<version>`` pin.

    Any PEP 440 local-version segment (after ``+``) is dropped, since local versions are
    never available from a package index and so could not be installed by ``uvx``.
    """
    import importlib.metadata

    try:
        version = importlib.metadata.version("repren")
    except importlib.metadata.PackageNotFoundError:
        version = "0.0.0.dev"
    return version.split("+", 1)[0]


def _render_skill(template: str) -> str:
    """Substitute the version placeholder in the skill template.

    The installed repren version is injected so the skill's pinned
    ``uvx repren@<version>`` fallback matches the package that produced it.
    """
    return template.replace(VERSION_PLACEHOLDER, _pinned_version())


def get_skill_content() -> str:
    """Read SKILL.md from package data and render it for the installed version.

    Returns:
        The rendered SKILL.md content, with ``{{REPREN_VERSION}}`` replaced by the
        installed repren version.

    Raises:
        ImportError: If package resources cannot be accessed.
        FileNotFoundError: If SKILL.md cannot be found in package data.
    """
    try:
        # Python 3.9+ importlib.resources API
        from importlib.resources import files

        skill_file = files("repren").joinpath("skills/SKILL.md")
        template = skill_file.read_text(encoding="utf-8")
    except (ImportError, AttributeError):
        # Fallback for older Python versions
        try:
            import pkg_resources  # type: ignore[import-not-found]  # pyright: ignore[reportMissingImports]

            template = pkg_resources.resource_string("repren", "skills/SKILL.md").decode("utf-8")
        except Exception as e:
            raise ImportError(
                f"Could not load skill from package data: {e}\n"
                "Ensure repren is installed as a package, not run as a standalone script."
            ) from e

    return _render_skill(template)


def _resolve_root(agent_base: str | None) -> tuple[Path, str]:
    """Resolve the root directory the skill surfaces are installed under.

    The skill is always written to two surfaces beneath the returned root:
    ``<root>/.agents/skills/repren/`` (portable, cross-agent) and
    ``<root>/.claude/skills/repren/`` (Claude Code mirror).

    Args:
        agent_base: None for a global install (under ``$HOME``). Otherwise the project
            root, or — for backward compatibility — a ``.claude``/``.agents`` directory
            whose parent is taken as the project root.

    Returns:
        A ``(root, scope_description)`` tuple.
    """
    if agent_base is None:
        return Path.home(), "globally (under ~)"

    resolved = Path(agent_base).resolve()
    # Backward compatibility: callers historically passed the `.claude` dir itself
    # (e.g. `--agent-base ./.claude`). Treat such a path as "the project is its parent".
    if resolved.name in (".agents", ".claude"):
        resolved = resolved.parent
    return resolved, f"to project {resolved}"


def install_skill(agent_base: str | None = None) -> None:
    """Install the repren skill for coding agents.

    Writes the skill to both the portable cross-agent surface and the Claude Code
    mirror, under the resolved root:

    - ``<root>/.agents/skills/repren/SKILL.md`` (portable: Codex, pi, and others)
    - ``<root>/.claude/skills/repren/SKILL.md`` (Claude Code)

    Args:
        agent_base: None (default) installs globally under ``$HOME``. Pass a project
            root (or a ``.claude``/``.agents`` directory inside it) for a project-local
            install that can be committed and shared with your team.
    """
    root, scope_desc = _resolve_root(agent_base)

    # Load and render skill content from package data
    try:
        skill_content = get_skill_content()
    except (ImportError, FileNotFoundError) as e:
        print(f"\n✗ Error: Could not load skill content: {e}", file=sys.stderr)
        print("\nThis command requires repren to be installed as a package.", file=sys.stderr)
        print("Install with: uv tool install repren", file=sys.stderr)
        sys.exit(1)

    # Two surfaces: portable canonical + Claude Code mirror.
    targets = [
        ("portable", root / ".agents" / "skills" / "repren" / "SKILL.md"),
        ("Claude Code", root / ".claude" / "skills" / "repren" / "SKILL.md"),
    ]

    try:
        written: list[Path] = []
        for _label, skill_file in targets:
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(skill_content, encoding="utf-8")
            written.append(skill_file)

        print("\n" + "=" * 70)
        print(f"✓ Repren skill installed {scope_desc}")
        print("=" * 70)
        print("\nLocations:")
        for skill_file in written:
            print(f"  {skill_file}")
        print("\nCoding agents will now use repren for refactoring tasks.")
        print("To uninstall, remove the repren/ directories above.")

        # Show tip for project installs (when not using default global location)
        if agent_base is not None:
            print("\n" + "-" * 70)
            print("Tip: Commit .agents/skills/ and .claude/skills/ to share this with your team.")
            print("-" * 70)

        print()  # Blank line for clean output

    except PermissionError as e:
        print(f"\n✗ Permission denied: {e}", file=sys.stderr)
        print(f"\nCould not write under {root}", file=sys.stderr)
        print("Check directory permissions and try again.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"\n✗ Installation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Command-line interface for skill installation.

    Can be run directly for testing:
        python -m repren.claude_skill
        python -m repren.claude_skill --agent-base ./.claude
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Install repren agent skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Install globally (under ~)
  %(prog)s --agent-base .         # Install in current project
  %(prog)s --agent-base ./.claude # Install in current project (legacy form)
        """,
    )

    parser.add_argument(
        "--agent-base",
        dest="agent_base",
        metavar="DIR",
        help="project root for a project-local install (defaults to a global install under ~)",
    )

    args = parser.parse_args()

    install_skill(agent_base=args.agent_base)


if __name__ == "__main__":
    main()
