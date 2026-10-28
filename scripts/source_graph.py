"""Stage explicitly pinned archives into a fresh tree for future multi-source builds.

This is a staging primitive only. Existing recipe, source-bundle and release
checks still reject external graphs until their integration is reviewed.
"""
from __future__ import annotations

import configparser
import os
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from common import ScaffoldError, fetch_pinned_archive

MAX_EXPANDED_BYTES = 1024 * 1024 * 1024


def unpack_archive(archive_path: Path, destination: Path) -> None:
    """Unpack a single-root archive without links, special files or overwrites."""
    root_name: str | None = None
    seen: set[tuple[str, ...]] = set()
    total = 0
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            raw = member.name
            parts = PurePosixPath(raw).parts
            if not parts or raw.startswith("/") or "\\" in raw or any(p in (".", "..", ".git") for p in parts):
                raise ScaffoldError(f"Unsafe source archive member: {raw}")
            if root_name is None:
                root_name = parts[0]
            if parts[0] != root_name:
                raise ScaffoldError("Source archive must have exactly one top-level directory")
            if not (member.isdir() or member.isfile()):
                raise ScaffoldError(f"Unsupported source archive member: {raw}")
            relative = parts[1:]
            if not relative:
                if not member.isdir():
                    raise ScaffoldError("Source archive root must be a directory")
                continue
            if relative in seen:
                raise ScaffoldError(f"Duplicate source archive member: {raw}")
            seen.add(relative)
            target = destination.joinpath(*relative)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            total += member.size
            if member.size < 0 or total > MAX_EXPANDED_BYTES:
                raise ScaffoldError("Expanded source archive exceeds size limit")
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = archive.extractfile(member)
            if handle is None:
                raise ScaffoldError(f"Cannot read source archive member: {raw}")
            with handle, target.open("xb") as output:
                shutil.copyfileobj(handle, output)
            os.chmod(target, 0o755 if member.mode & 0o111 else 0o644)
    if root_name is None:
        raise ScaffoldError("Empty source archive")


def validate_submodule_paths(tree: Path, paths: list[tuple[str, ...]]) -> None:
    """Reject any declared git submodule not explicitly staged at its path.

    Archive files do not contain gitlink commits, so callers must independently
    verify revisions against the upstream Git tree; this is not a completeness
    or license review.
    """
    declared: set[tuple[str, ...]] = set()
    for modules in tree.rglob(".gitmodules"):
        parser = configparser.ConfigParser(interpolation=None, strict=True)
        try:
            with modules.open(encoding="utf-8") as handle:
                parser.read_file(handle)
            for section in parser.sections():
                if not section.startswith('submodule "') or not section.endswith('"'):
                    raise ScaffoldError(f"Unexpected submodule declaration in {modules}")
                value = parser.get(section, "path")
                relative = PurePosixPath(value).parts
                if (not relative or value.startswith("/") or "\\" in value
                        or ".." in relative):
                    raise ScaffoldError(f"Unsafe git submodule path: {value!r}")
                full = modules.parent.relative_to(tree).parts + relative
                if full in declared or full not in paths:
                    raise ScaffoldError(f"Unstaged or duplicate git submodule: {'/'.join(full)}")
                declared.add(full)
        except (configparser.Error, UnicodeError) as error:
            raise ScaffoldError(f"Invalid git submodule declaration in {modules}: {error}") from error


def stage_graph(primary_name: str, primary: dict[str, Any], additional: list[dict[str, Any]],
                cache: Path, destination: Path) -> None:
    """Fetch and stage a root source plus named sources at explicit empty paths.

    Each additional entry has ``name``, ``path``, ``commit``, ``sha256`` and
    ``url``. Installation paths cannot overlap, and staging is atomic: failure
    leaves no destination. This does not validate licenses, discover missing
    sources, disable network fetches or authorize a release.
    """
    if destination.exists() or destination.is_symlink():
        raise ScaffoldError("Source staging destination already exists")
    paths: list[tuple[str, ...]] = []
    names = {primary_name}
    for entry in additional:
        name, raw = entry["name"], entry["path"]
        parts = PurePosixPath(raw).parts
        if not parts or raw.startswith("/") or "\\" in raw or any(p in (".", "..", ".git") for p in parts):
            raise ScaffoldError(f"Unsafe staging path: {raw!r}")
        if name in names:
            raise ScaffoldError(f"Duplicate source name: {name}")
        if any(parts[:len(other)] == other or other[:len(parts)] == parts for other in paths):
            raise ScaffoldError(f"Overlapping staging path: {raw}")
        names.add(name)
        paths.append(parts)
    root_archive = fetch_pinned_archive(primary_name, primary, cache)
    archives = [fetch_pinned_archive(entry["name"], entry, cache) for entry in additional]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".source-stage-", dir=destination.parent) as temp:
        tree = Path(temp) / "tree"
        tree.mkdir()
        unpack_archive(root_archive, tree)
        for path, source in zip(paths, archives):
            target = tree.joinpath(*path)
            if target.exists() and (not target.is_dir() or any(target.iterdir())):
                raise ScaffoldError(f"Staging path is not empty: {'/'.join(path)}")
            target.mkdir(parents=True, exist_ok=True)
            unpack_archive(source, target)
        validate_submodule_paths(tree, paths)
        tree.rename(destination)
