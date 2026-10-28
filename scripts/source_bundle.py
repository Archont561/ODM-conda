#!/usr/bin/env python3
"""Create a deterministic, hash-checked source + packaging archive.

Single-archive components are supported. A source-completeness review is
still required before distribution: this script is not a legal certification.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

from common import ROOT, ScaffoldError, config, fail_cli, repository_files, select_components, sha256, source_archive, source_bundle_name


def validate_upstream_archive(path: Path, disabled_build_trees: tuple[str, ...] = ()) -> None:
    """Reject undisclosed fetches in enabled targets; keep disabled test sources intact."""
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            parts = PurePosixPath(member.name).parts
            if not parts or member.name.startswith("/") or ".." in parts or "\\" in member.name:
                raise ScaffoldError(f"Unsafe source archive member: {member.name}")
            if member.issym() or member.islnk():
                raise ScaffoldError("Starter source archives must not contain links; review handling before extending")
            if member.isfile() and parts[-1] == ".gitmodules":
                raise ScaffoldError("Source contains submodules; a single GitHub archive is insufficient")
            if member.isfile() and (parts[-1] == "CMakeLists.txt" or parts[-1].endswith(".cmake")):
                relative_parts = parts[1:]  # GitHub archives have one top-level source directory.
                if relative_parts and relative_parts[0] in disabled_build_trees:
                    continue  # These sources remain in the original archive; only fetch scanning is skipped.
                handle = archive.extractfile(member)
                assert handle is not None
                text = handle.read().lower().replace(b" ", b"").replace(b"\n", b"")
                if any(token in text for token in (b"externalproject_add(", b"fetchcontent_", b"file(download")):
                    raise ScaffoldError(f"Unstaged external CMake source in {member.name}")


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes, mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.mode = mode
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def make_bundle(name: str, component: dict, destination: Path, cache: Path, root: Path = ROOT) -> Path:
    source = source_archive(name, component, cache)
    validate_upstream_archive(source, tuple(component["source"].get("disabled_build_trees", [])))
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / source_bundle_name(name, component)
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = None
    # Exclude generated validation reports: each bundle includes the maintained
    # scripts, tests, recipes and lockfile, plus the exact upstream archive.
    files = repository_files(root)
    entries: dict[str, bytes] = {f"packaging/{p.relative_to(root).as_posix()}": p.read_bytes() for p in files}
    archive_name = f"upstream/{name}-{component['source']['commit']}.tar.gz"
    entries[archive_name] = source.read_bytes()
    manifest = {"schema_version": 1, "component": name, "version": component["version"],
                "build_number": component["build_number"], "packaging_commit": revision,
                "upstream": component["source"],
                "files": {key: hashlib.sha256(value).hexdigest() for key, value in sorted(entries.items())}}
    entries["SOURCE-MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    entries["README-SOURCE.txt"] = (
        f"Source bundle for {name} {component['version']}, build {component['build_number']}\n\n"
        "upstream/ contains the exact hash-verified upstream archive, including its vendored code.\n"
        "packaging/ contains recipes, original build/test scripts, license handling, and the Pixi tool lock.\n"
        "SOURCE-MANIFEST.json lists file checksums and the packaging revision when available.\n\n"
        "Rebuild: extract this bundle; enter packaging/; run `pixi install --locked`;\n"
        f"then `pixi run build --component {name}`. Network access is used for Conda dependencies\n"
        "and the recipe's hash-checked source URL. To use the included source offline, unpack\n"
        "its upstream archive and change a COPY of the recipe's source to `path: /absolute/source/tree`\n"
        "(remove url/sha256); rerun rattler-build with that recipe. Source path checks in lint\n"
        "are intentionally strict for maintained release recipes, not such local rebuild copies.\n\n"
        "Enabled starter targets have no undisclosed source downloads. FPCFilter BUILD_TESTING=OFF\n"
        "excludes its test-only GoogleTest fetch from the build, not from the original source archive.\n"
        "The bundle does not include Conda dependency binaries or certify which third-party\n"
        "sources a particular distribution must additionally provide. Review applicable obligations.\n"
        "The MIT packaging license does not relicense upstream code or upstream-derived patches.\n"
    ).encode()
    temporary = target.with_suffix(target.suffix + ".tmp")
    try:
        with temporary.open("wb") as output:
            with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                    for key, value in sorted(entries.items()):
                        add_bytes(archive, key, value)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Source bundle: {target}\nSHA256: {sha256(target)}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "source-bundles")
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "sources")
    options = parser.parse_args()
    for name, component in select_components(options.component).items():
        make_bundle(name, component, options.output_dir, options.cache)


if __name__ == "__main__":
    fail_cli(main)
