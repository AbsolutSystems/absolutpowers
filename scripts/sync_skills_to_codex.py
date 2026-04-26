#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_SKILLS_DIR = REPO_ROOT / "skills"
TARGET_SKILLS_DIR = REPO_ROOT / "plugins" / "absolutpowers" / "skills"
FRONTMATTER_KEYS_TO_DROP = {
    "allowed-tools",
    "argument-hint",
}


def transform_skill_markdown(content: str) -> str:
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return content

    end_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return content

    frontmatter = []
    for line in lines[1:end_index]:
        stripped = line.lstrip()
        if any(stripped.startswith(f"{key}:") for key in FRONTMATTER_KEYS_TO_DROP):
            continue
        frontmatter.append(line)

    return "".join([lines[0], *frontmatter, lines[end_index], *lines[end_index + 1 :]])


def sync_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.name == "SKILL.md":
        content = source.read_text(encoding="utf-8")
        target.write_text(transform_skill_markdown(content), encoding="utf-8")
        return

    shutil.copy2(source, target)


def remove_stale_files(source_root: Path, target_root: Path) -> int:
    removed = 0
    for target_path in sorted(target_root.rglob("*"), reverse=True):
        relative_path = target_path.relative_to(target_root)
        source_path = source_root / relative_path
        if source_path.exists():
            continue
        if target_path.is_file():
            target_path.unlink()
            removed += 1
        elif target_path.is_dir():
            target_path.rmdir()
    return removed


def sync_skills(source_root: Path, target_root: Path) -> tuple[int, int]:
    copied = 0
    for source_path in sorted(source_root.rglob("*")):
        if source_path.is_dir():
            continue
        relative_path = source_path.relative_to(source_root)
        target_path = target_root / relative_path
        sync_file(source_path, target_path)
        copied += 1

    removed = remove_stale_files(source_root, target_root)
    return copied, removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync repository skill sources into the Codex plugin bundle, "
            "dropping Claude-specific frontmatter fields from SKILL.md files."
        )
    )
    parser.add_argument(
        "--source",
        default=str(SOURCE_SKILLS_DIR),
        help="Source skills directory. Defaults to ./skills in this repository.",
    )
    parser.add_argument(
        "--target",
        default=str(TARGET_SKILLS_DIR),
        help="Target plugin skills directory. Defaults to ./plugins/absolutpowers/skills.",
    )
    args = parser.parse_args()

    source_root = Path(args.source).resolve()
    target_root = Path(args.target).resolve()

    if not source_root.exists():
        raise SystemExit(f"Source skills directory does not exist: {source_root}")

    target_root.mkdir(parents=True, exist_ok=True)
    copied, removed = sync_skills(source_root, target_root)
    print(f"Synced {copied} file(s) from {source_root} to {target_root}")
    print(f"Removed {removed} stale file(s) from {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
