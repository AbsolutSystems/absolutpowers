#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


AGENTS_BANNER = (
    "> Generated from the sibling `CLAUDE.md` file.\n"
    "> Edit `CLAUDE.md`, then re-run the AI context sync to refresh this mirror.\n\n"
)

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    ".venv",
    "venv",
    "__pycache__",
}


def iter_claude_files(root: Path) -> list[Path]:
    claude_files: list[Path] = []
    for path in root.rglob("CLAUDE.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        claude_files.append(path)
    return sorted(claude_files)


def mirror_file(source: Path) -> Path:
    target = source.with_name("AGENTS.md")
    content = source.read_text(encoding="utf-8")
    target.write_text(AGENTS_BANNER + content, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror every CLAUDE.md under a project root into a sibling AGENTS.md."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Target project root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.exists():
        raise SystemExit(f"Project root does not exist: {root}")

    mirrored = [mirror_file(path) for path in iter_claude_files(root)]
    print(f"Mirrored {len(mirrored)} file(s) from CLAUDE.md to AGENTS.md under {root}")
    for target in mirrored:
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
