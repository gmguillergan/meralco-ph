#!/usr/bin/env python3
"""
Bump the project version.

The version lives in src/__init__.py (__version__), which is the single source of
truth. config.yaml (Home Assistant add-on) must carry the same literal version, so
this script updates both. src/api.py derives its version from __version__ at runtime.

Usage:
  python scripts/bump_version.py 1.2.0     # set exact version
  python scripts/bump_version.py major     # 1.1.2 -> 2.0.0
  python scripts/bump_version.py minor     # 1.1.2 -> 1.2.0
  python scripts/bump_version.py patch     # 1.1.2 -> 1.1.3
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def get_current_version() -> str:
    init_py = ROOT / "src" / "__init__.py"
    if not init_py.exists():
        sys.exit(f"Missing: {init_py}")
    match = re.search(r'__version__\s*=\s*"([^"]*)"', init_py.read_text())
    if not match or not VERSION_RE.match(match.group(1)):
        sys.exit("Could not read current version from src/__init__.py")
    return match.group(1)


def bump_part(current: str, part: str) -> str:
    major, minor, patch = (int(x) for x in current.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(part)


def apply_version(version: str) -> None:
    init_py = ROOT / "src" / "__init__.py"
    config_yaml = ROOT / "config.yaml"

    for path in (init_py, config_yaml):
        if not path.exists():
            sys.exit(f"Missing: {path}")

    text = init_py.read_text()
    text = re.sub(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"', text)
    init_py.write_text(text)
    print(f"Updated {init_py.relative_to(ROOT)}")

    text = config_yaml.read_text()
    text = re.sub(r'^version:\s*"[^"]*"', f'version: "{version}"', text, flags=re.M)
    config_yaml.write_text(text)
    print(f"Updated {config_yaml.relative_to(ROOT)}")

    print(f"Version set to {version}")
    print("Don't forget to update CHANGELOG.md, then run scripts/check_versions.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/bump_version.py <version|major|minor|patch>")
    arg = sys.argv[1].lower()
    if arg in ("major", "minor", "patch"):
        current = get_current_version()
        version = bump_part(current, arg)
        print(f"Bumping {arg}: {current} -> {version}")
    elif VERSION_RE.match(arg):
        version = arg
    else:
        sys.exit(
            f"Invalid argument: {arg!r}. Use a version (e.g. 1.2.0) or major|minor|patch"
        )
    apply_version(version)
