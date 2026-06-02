#!/usr/bin/env python
"""
Sync documentation from docs/repren-docs.md to repren/repren.py and README.md.

The manual is the single source of truth. This script:
1. Updates the docstring in repren/repren.py
2. Updates the documentation section in README.md

The manual may use the ``{{REPREN_VERSION}}`` placeholder anywhere it shows a pinned
``uvx repren@<version>`` invocation; this script substitutes the current version so the
docs stay pinned (supply-chain hygiene) without anyone hand-editing version strings. The
version is resolved from, in order: ``REPREN_DOCS_VERSION`` (release automation), the
installed package version when it is a clean release, then ``DEFAULT_DOC_VERSION``.
"""

import importlib.metadata
import os
import re
import sys
from pathlib import Path

# Placeholder used in the manual for the pinned repren version (matches claude_skill).
VERSION_PLACEHOLDER = "{{REPREN_VERSION}}"

# Fallback shown in docs when no released package version is resolvable (e.g. an editable
# dev checkout). Set to the version currently being prepared; release builds override it
# automatically with the real package version, so this rarely needs touching.
DEFAULT_DOC_VERSION = "2.1.0"


def _is_clean_release(version: str) -> bool:
    """True for a published release version (no dev/pre-release or local segment)."""
    return bool(re.fullmatch(r"\d+\.\d+(?:\.\d+)?", version))


def get_doc_version() -> str:
    """Resolve the version to pin in generated docs.

    Order: ``REPREN_DOCS_VERSION`` env override → installed package version (only if it is
    a clean release) → ``DEFAULT_DOC_VERSION``.
    """
    override = os.environ.get("REPREN_DOCS_VERSION")
    if override:
        return override.lstrip("v")

    try:
        version = importlib.metadata.version("repren")
        if _is_clean_release(version):
            return version
    except importlib.metadata.PackageNotFoundError:
        pass

    return DEFAULT_DOC_VERSION


def render_version(text: str, version: str) -> str:
    """Substitute the version placeholder in manual text."""
    return text.replace(VERSION_PLACEHOLDER, version)


def read_manual(repo_root: Path) -> str:
    """Read the manual content."""
    manual_path = repo_root / "docs" / "repren-docs.md"
    return manual_path.read_text()


def update_repren_py(repo_root: Path, manual: str) -> bool:
    """Update the docstring in repren/repren.py."""
    repren_path = repo_root / "repren" / "repren.py"
    content = repren_path.read_text()

    # Match from opening """ or r""" to closing """ (the docstring)
    # The docstring starts right after #!/usr/bin/env python
    pattern = r'^(#!/usr/bin/env python\n)r?"""\n.*?(""")'
    match = re.search(pattern, content, flags=re.DOTALL)

    if not match:
        print("ERROR: Could not find docstring pattern in repren.py", file=sys.stderr)
        return False

    # Build new content using string concatenation (not re.sub) to avoid
    # backreference issues with \1, \2, etc. in the manual
    # Use r""" raw string to preserve backslashes in documentation
    new_content = match.group(1) + 'r"""\n' + manual + match.group(2) + content[match.end() :]

    if new_content != content:
        repren_path.write_text(new_content)
        print(f"Updated: {repren_path}")
    else:
        print(f"No changes: {repren_path}")

    return True


# Pinned-version invocations in the hand-written README header (e.g. the agent
# quick-start), normalized to the current version on each run so the header stays in sync
# without manual edits. Scoped to the header only, which never mentions `@latest`.
_HEADER_PIN_RE = re.compile(r"uvx repren@[A-Za-z0-9][A-Za-z0-9._-]*")


def update_readme(repo_root: Path, manual: str, version: str) -> bool:
    """Update the documentation section in README.md."""
    readme_path = repo_root / "README.md"
    content = readme_path.read_text()

    # README structure:
    # - Header (# repren, image, * * *, announcement, * * *)
    # - Documentation (## Rename Anything ... through notes)
    # - Footer (## Contributing, ## License, etc.)
    #
    # Match from after the second "* * *" to before "\n## Contributing"
    pattern = r"(\* \* \*\n\n)(## Rename Anything.*?)(\n## Contributing)"
    match = re.search(pattern, content, flags=re.DOTALL)

    if not match:
        print("ERROR: Could not find documentation section in README.md", file=sys.stderr)
        return False

    # The hand-written header is not regenerated from the manual, so normalize any
    # `uvx repren@<version>` pins in it to the current version (idempotent).
    header = _HEADER_PIN_RE.sub(f"uvx repren@{version}", content[: match.start()])

    # Build new content using string concatenation (not re.sub) to avoid
    # backreference issues with \1, \2, etc. in the manual
    new_content = header + match.group(1) + manual + match.group(3) + content[match.end() :]

    if new_content != content:
        readme_path.write_text(new_content)
        print(f"Updated: {readme_path}")
    else:
        print(f"No changes: {readme_path}")

    return True


def main() -> int:
    repo_root = Path(__file__).parent.parent

    print("Reading manual from docs/repren-docs.md...")
    manual = read_manual(repo_root)

    version = get_doc_version()
    print(f"Pinning docs to repren version: {version}")
    manual = render_version(manual, version)

    success = True
    success = update_repren_py(repo_root, manual) and success
    success = update_readme(repo_root, manual, version) and success

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
