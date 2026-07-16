"""File organization engine for FolderWise AI.

Pure local filesystem operations - no cloud, no network. Designed so a future
offline desktop AI assistant can swap in smarter categorization without
changing the execute/undo machinery.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from config import (
    CATEGORIES,
    CATEGORY_ORDER,
    EXTENSION_SORT_PHRASES,
    INSTRUCTION_KEYWORDS,
    ORGANIZED_ROOT_NAME,
)


def build_extension_index() -> Dict[str, str]:
    """Reverse map: extension -> category name."""
    index: Dict[str, str] = {}
    for category, exts in CATEGORIES.items():
        for ext in exts:
            index[ext.lower().lstrip(".")] = category
    return index


_EXT_INDEX = build_extension_index()


def categorize_extension(ext: str) -> str:
    """Return the category name for a file extension, or 'Others'."""
    return _EXT_INDEX.get(ext.lower().lstrip("."), "Others")


@dataclass
class FileEntry:
    path: str          # absolute source path
    name: str          # base filename
    ext: str          # lowercase extension without dot
    size: int          # bytes
    category: str      # resolved category

    def destination_folder(self, root: Path) -> Path:
        return root / self.category

    def destination_path(self, root: Path) -> Path:
        return self.destination_folder(root) / self.name


@dataclass
class PreviewPlan:
    """Snapshot of what an organization would do."""
    source_dir: str
    organized_root: str
    total_files: int
    total_size: int
    by_category: Dict[str, List[FileEntry]] = field(default_factory=dict)
    new_folders: List[str] = field(default_factory=list)
    # How files are grouped: "category" or "extension"
    grouping: str = "category"
    # Human-readable label for each destination folder -> display name
    folder_labels: Dict[str, str] = field(default_factory=dict)

    def category_counts(self) -> Dict[str, int]:
        return {cat: len(files) for cat, files in self.by_category.items()}

    def category_sizes(self) -> Dict[str, int]:
        return {cat: sum(f.size for f in files) for cat, files in self.by_category.items()}


def scan_directory(source_dir: str) -> List[FileEntry]:
    """List all files (non-recursive) in source_dir, skipping the organized root."""
    source = Path(source_dir)
    if not source.is_dir():
        return []

    entries: List[FileEntry] = []
    for item in sorted(source.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_file():
            continue
        ext = item.suffix.lstrip(".").lower()
        entries.append(
            FileEntry(
                path=str(item),
                name=item.name,
                ext=ext,
                size=item.stat().st_size,
                category=categorize_extension(ext),
            )
        )
    return entries


def parse_instruction(instruction: str) -> Tuple[Optional[str], Optional[Set[str]], bool]:
    """Parse a natural-language instruction into a filter spec.

    Returns (category_filter, extension_filter, sort_by_extension).
    - category_filter: restrict to this category, or None for all.
    - extension_filter: restrict to these extensions within the category, or None.
    - sort_by_extension: group by extension instead of category.
    """
    text = instruction.lower().strip()
    if not text:
        return None, None, False

    # Check for extension-sort phrases first.
    for phrase in EXTENSION_SORT_PHRASES:
        if phrase in text:
            return None, None, True

    # Keyword matching (longest keywords first for "zip files" > "zip").
    for keyword in sorted(INSTRUCTION_KEYWORDS.keys(), key=len, reverse=True):
        if keyword in text:
            value = INSTRUCTION_KEYWORDS[keyword]
            if value is None:
                return None, None, False
            if isinstance(value, tuple):
                cat, exts = value
                return cat, exts, False
            return value, None, False

    return None, None, False


def build_plan(
    source_dir: str,
    instruction: str = "",
    mode: str = "subfolder",
    subfolder_name: str = "",
) -> PreviewPlan:
    """Scan the directory and produce a plan.

    Args:
        source_dir: directory to organize.
        instruction: natural-language instruction for filtering/grouping.
        mode: "subfolder" (move into a new subfolder) or "inplace" (organize
            directly inside source_dir).
        subfolder_name: custom name for the organized subfolder. If empty,
            uses the default ORGANIZED_ROOT_NAME. Ignored when mode="inplace".
    """
    entries = scan_directory(source_dir)
    source = Path(source_dir)

    cat_filter, ext_filter, sort_by_ext = parse_instruction(instruction)

    # Apply instruction filters.
    if cat_filter is not None:
        entries = [e for e in entries if e.category == cat_filter]
    if ext_filter is not None:
        entries = [e for e in entries if e.ext in ext_filter]

    grouping = "extension" if sort_by_ext else "category"

    # Determine the organized root.
    if mode == "inplace":
        organized_root = source
    else:
        folder = subfolder_name.strip() or ORGANIZED_ROOT_NAME
        organized_root = source / folder

    # Group files.
    by_group: Dict[str, List[FileEntry]] = {}
    folder_labels: Dict[str, str] = {}

    if grouping == "extension":
        for entry in entries:
            key = entry.ext if entry.ext else "no_extension"
            by_group.setdefault(key, []).append(entry)
            folder_labels[key] = f".{key}" if key != "no_extension" else "(no extension)"
    else:
        for cat in CATEGORY_ORDER:
            by_group[cat] = []
        for entry in entries:
            by_group[entry.category].append(entry)
        for cat in CATEGORY_ORDER:
            folder_labels[cat] = cat

    # New folders (only non-empty groups).
    new_folders: List[str] = []
    for key, files in by_group.items():
        if files:
            new_folders.append(str(organized_root / key))

    return PreviewPlan(
        source_dir=source_dir,
        organized_root=str(organized_root),
        total_files=len(entries),
        total_size=sum(e.size for e in entries),
        by_category=by_group,
        new_folders=new_folders,
        grouping=grouping,
        folder_labels=folder_labels,
    )


def _manifest_path(source_dir: str, organized_root: str) -> Path:
    return Path(organized_root) / "_folderwise_manifest.json"


def execute_plan(plan: PreviewPlan) -> Dict:
    """Execute the plan: create folders, move files, write a manifest for undo.

    Returns a manifest dict describing every move (source -> dest).
    """
    organized_root = Path(plan.organized_root)
    # Only mkdir if we're creating a subfolder; in-place mode uses source dir.
    if str(organized_root) != plan.source_dir:
        organized_root.mkdir(parents=True, exist_ok=True)

    moves: List[Dict[str, str]] = []
    for group_key, files in plan.by_category.items():
        if not files:
            continue
        dest_folder = organized_root / group_key
        dest_folder.mkdir(exist_ok=True)
        for entry in files:
            dest = dest_folder / entry.name
            # Avoid clobbering same-named files across groups.
            if dest.exists() and dest.resolve() != Path(entry.path).resolve():
                stem, suffix = dest.stem, dest.suffix
                i = 1
                while dest.exists():
                    dest = dest.with_name(f"{stem}_{i}{suffix}")
                    i += 1
            shutil.move(entry.path, dest)
            moves.append({"src": entry.path, "dest": str(dest), "group": group_key})

    manifest = {
        "created_at": time.time(),
        "source_dir": plan.source_dir,
        "organized_root": plan.organized_root,
        "moves": moves,
    }
    _manifest_path(plan.source_dir, plan.organized_root).write_text(json.dumps(manifest, indent=2))
    return manifest


def undo_last(source_dir: str) -> Optional[Dict]:
    """Restore files to their original locations using the manifest.

    Searches for a manifest inside any organized subfolder of source_dir, or
    directly in source_dir (in-place mode). Returns the manifest that was
    undone, or None if no manifest exists.
    """
    source = Path(source_dir)
    manifest_file: Optional[Path] = None

    # In-place mode: manifest lives directly in source_dir.
    direct = source / "_folderwise_manifest.json"
    if direct.exists():
        manifest_file = direct

    # Subfolder mode: manifest inside a child folder.
    if manifest_file is None:
        for child in source.iterdir():
            candidate = child / "_folderwise_manifest.json"
            if candidate.exists():
                manifest_file = candidate
                break

    if manifest_file is None:
        return None

    manifest = json.loads(manifest_file.read_text())
    organized_root = Path(manifest["organized_root"])

    for move in reversed(manifest["moves"]):
        src = Path(move["dest"])
        original = Path(move["src"])
        if src.exists():
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(original))

    # Remove the manifest first so the organized root can be removed if empty.
    manifest_file.unlink(missing_ok=True)

    # Remove now-empty group folders, then the organized root if it's a
    # subfolder (not the source dir itself).
    if organized_root.exists() and str(organized_root) != source_dir:
        for child in sorted(organized_root.iterdir(), reverse=True):
            if child.is_dir():
                try:
                    child.rmdir()
                except OSError:
                    pass
        try:
            organized_root.rmdir()
        except OSError:
            pass

    return manifest


def human_size(num_bytes: int) -> str:
    """Human-readable byte size."""
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
