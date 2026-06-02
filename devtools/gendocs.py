#!/usr/bin/env python
"""
Sync documentation from docs/repren-docs.md to repren/repren.py and README.md.

The manual is the single source of truth. This script:
1. Updates the docstring in repren/repren.py
2. Updates the documentation section in README.md
"""

import re
import sys
from pathlib import Path


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


def update_readme(repo_root: Path, manual: str) -> bool:
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

    # Build new content using string concatenation (not re.sub) to avoid
    # backreference issues with \1, \2, etc. in the manual
    new_content = (
        content[: match.start()] + match.group(1) + manual + match.group(3) + content[match.end() :]
    )

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

    success = True
    success = update_repren_py(repo_root, manual) and success
    success = update_readme(repo_root, manual) and success

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
