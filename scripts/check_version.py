#!/usr/bin/env python3
"""Version-consistency guard.

Compares `pyproject.toml`'s `[tool.poetry].version` against:

1. The newest numbered `## [x.y.z]` heading in `CHANGELOG.md`.
2. `setup.py`'s hardcoded `version="..."` string, if present.

Run with no arguments to check consistency (used in CI on every push/PR).
Run with `--tag <ref>` to additionally check a release tag (e.g. `v0.10.0`
or `refs/tags/v0.10.0`) against the pyproject version; used by the publish
workflow immediately before publishing, so a release cut from the wrong
commit fails loudly instead of shipping.

Exit code is non-zero, with a message on stderr, on any mismatch.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
SETUP_PY = REPO_ROOT / "setup.py"


def _read_pyproject_version() -> str:
    text = PYPROJECT.read_text()
    # Only match within the [tool.poetry] table's own version key, which is
    # the first `version = "..."` line in the file for this project's
    # pyproject.toml layout.
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not match:
        raise SystemExit(f"Could not find a version in {PYPROJECT}")
    return match.group(1)


def _read_changelog_version() -> str:
    text = CHANGELOG.read_text()
    match = re.search(r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]", text)
    if not match:
        raise SystemExit(f"Could not find a numbered '## [x.y.z]' heading in {CHANGELOG}")
    return match.group(1)


def _read_setup_py_version() -> str | None:
    if not SETUP_PY.exists():
        return None
    text = SETUP_PY.read_text()
    match = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def _normalize_tag(tag: str) -> str:
    tag = tag.strip()
    if tag.startswith("refs/tags/"):
        tag = tag[len("refs/tags/"):]
    if tag.startswith("v"):
        tag = tag[1:]
    return tag


def main(argv: list[str]) -> int:
    pyproject_version = _read_pyproject_version()
    changelog_version = _read_changelog_version()
    setup_py_version = _read_setup_py_version()

    errors = []

    if pyproject_version != changelog_version:
        errors.append(
            f"pyproject.toml version ({pyproject_version}) does not match the "
            f"newest CHANGELOG.md heading ({changelog_version})."
        )

    if setup_py_version is not None and setup_py_version != pyproject_version:
        errors.append(
            f"setup.py version ({setup_py_version}) does not match "
            f"pyproject.toml version ({pyproject_version})."
        )

    if "--tag" in argv:
        tag_arg = argv[argv.index("--tag") + 1]
        tag_version = _normalize_tag(tag_arg)
        if tag_version != pyproject_version:
            errors.append(
                f"Release tag ({tag_arg} -> {tag_version}) does not match "
                f"pyproject.toml version ({pyproject_version}). Refusing to publish."
            )

    if errors:
        for e in errors:
            print(f"::error::{e}", file=sys.stderr)
        return 1

    print(
        f"Version check OK: pyproject.toml={pyproject_version}, "
        f"CHANGELOG.md={changelog_version}"
        + (f", setup.py={setup_py_version}" if setup_py_version else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
