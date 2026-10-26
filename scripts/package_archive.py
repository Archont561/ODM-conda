"""Read small .conda artifacts without extracting untrusted paths.

The starter package audit intentionally rejects links/special files. Extend this
only with explicit path/link validation when larger component recipes need it.
"""
from __future__ import annotations

import json
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

from common import ScaffoldError

MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_MEMBERS = 10000


def validate_member(name: str) -> None:
    path = PurePosixPath(name)
    if not name or name.startswith("/") or ".." in path.parts or "\\" in name or ":" in name:
        raise ScaffoldError(f"Unsafe package member: {name!r}")


def read_package(path: Path) -> tuple[dict[str, bytes], dict[str, bytes]]:
    import zstandard

    groups: dict[str, dict[str, bytes]] = {"info": {}, "pkg": {}}
    total = count = 0
    with zipfile.ZipFile(path) as outer:
        members = outer.namelist()
        if len(members) != len(set(members)):
            raise ScaffoldError("Duplicate outer .conda ZIP member")
        metadata = json.loads(outer.read("metadata.json"))
        if metadata.get("conda_pkg_format_version") != 2:
            raise ScaffoldError("Expected .conda format version 2")
        selected = {}
        for kind in groups:
            archives = [name for name in members if name.startswith(kind + "-") and name.endswith(".tar.zst") and "/" not in name]
            if len(archives) != 1:
                raise ScaffoldError(f"Expected one {kind} tar.zst archive")
            selected[kind] = archives[0]
        if set(members) != {"metadata.json", *selected.values()}:
            raise ScaffoldError("Unexpected file in outer .conda ZIP")
        for kind, member_name in selected.items():
            with outer.open(member_name) as compressed:
                with zstandard.ZstdDecompressor().stream_reader(compressed) as decompressed:
                    with tarfile.open(fileobj=decompressed, mode="r|") as archive:
                        for member in archive:
                            count += 1
                            validate_member(member.name)
                            if count > MAX_MEMBERS:
                                raise ScaffoldError("Too many package members")
                            if member.isdir():
                                continue
                            if not member.isfile():
                                raise ScaffoldError(f"Links/special files are not allowed in starter packages: {member.name}")
                            if member.size > MAX_FILE or member.size < 0:
                                raise ScaffoldError("Package member size exceeds the audit limit")
                            total += member.size
                            if total > MAX_TOTAL:
                                raise ScaffoldError("Package contents exceed the audit limit")
                            if member.name in groups[kind]:
                                raise ScaffoldError("Duplicate package tar member")
                            handle = archive.extractfile(member)
                            assert handle is not None
                            groups[kind][member.name] = handle.read()
    return groups["info"], groups["pkg"]
