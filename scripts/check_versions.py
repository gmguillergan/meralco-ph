#!/usr/bin/env python3
"""
Verify the version is consistent across every place it is declared.

src/__init__.py (__version__) is the single source of truth. This checks that:
  - config.yaml `version:` matches it (Home Assistant pulls the image tag from here)
  - the top CHANGELOG.md entry matches it

Pass an expected version (with or without a leading "v") to also assert the release
tag matches, e.g. in CI:  python scripts/check_versions.py "${GITHUB_REF_NAME}"

Exits non-zero on any mismatch so a release never publishes with drifted versions.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_init() -> str:
    match = re.search(
        r'__version__\s*=\s*"([^"]*)"', (ROOT / "src" / "__init__.py").read_text()
    )
    if not match:
        sys.exit("Could not read __version__ from src/__init__.py")
    return match.group(1)


def read_config() -> str:
    match = re.search(
        r'^version:\s*"([^"]*)"', (ROOT / "config.yaml").read_text(), flags=re.M
    )
    if not match:
        sys.exit("Could not read version from config.yaml")
    return match.group(1)


def read_changelog() -> str:
    match = re.search(
        r"^## \[(\d+\.\d+\.\d+)\]", (ROOT / "CHANGELOG.md").read_text(), flags=re.M
    )
    if not match:
        sys.exit("Could not read latest version from CHANGELOG.md")
    return match.group(1)


def main() -> None:
    source = read_init()
    sources = {
        "src/__init__.py": source,
        "config.yaml": read_config(),
        "CHANGELOG.md (latest)": read_changelog(),
    }

    if len(sys.argv) > 1:
        sources["release tag"] = sys.argv[1].lstrip("v")

    for name, value in sources.items():
        print(f"{name:>24}: {value}")

    mismatched = {name: value for name, value in sources.items() if value != source}
    if mismatched:
        names = ", ".join(mismatched)
        sys.exit(f"\nVersion mismatch against src/__init__.py ({source}): {names}")

    print(f"\nAll version references agree: {source}")


if __name__ == "__main__":
    main()
