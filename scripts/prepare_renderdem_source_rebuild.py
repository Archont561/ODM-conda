#!/usr/bin/env python3
"""Verify a RenderDEM source bundle and prepare an isolated local-source recipe.

This is a reconstruction aid, not a license or corresponding-source attestation.
Conda-forge dependencies and Pixi tooling are still obtained separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path, PurePosixPath

from common import ScaffoldError, fail_cli, sha256
from source_graph import unpack_archive

MAX_ENTRY = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024


def prepare(bundle: Path, expected_sha256: str, destination: Path) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or sha256(bundle) != expected_sha256:
        raise ScaffoldError("Source bundle SHA256 does not match the independently supplied digest")
    if destination.exists():
        raise ScaffoldError("Reconstruction destination must not already exist")
    with tarfile.open(bundle, 'r:gz') as tar:
        entries = {}
        total = 0
        for entry in tar:
            parts = PurePosixPath(entry.name).parts
            if (not parts or entry.name.startswith('/') or '\\' in entry.name or '..' in parts
                    or entry.name != '/'.join(parts) or entry.name in entries or not entry.isfile()):
                raise ScaffoldError(f"Unsafe or duplicate bundle entry: {entry.name}")
            total += entry.size
            if entry.size < 0 or entry.size > MAX_ENTRY or total > MAX_TOTAL:
                raise ScaffoldError("Source bundle exceeds size limit")
            entries[entry.name] = entry
        if 'SOURCE-MANIFEST.json' not in entries or 'README-SOURCE.txt' not in entries:
            raise ScaffoldError("Source bundle is missing its manifest or README")
        def content(name: str) -> bytes:
            handle = tar.extractfile(entries[name])
            if handle is None:
                raise ScaffoldError(f"Cannot read bundle entry: {name}")
            with handle:
                return handle.read()
        manifest = json.loads(content('SOURCE-MANIFEST.json'))
        if manifest.get('schema_version') != 1 or manifest.get('component') != 'renderdem':
            raise ScaffoldError("Expected a RenderDEM source manifest")
        files = manifest.get('files')
        if not isinstance(files, dict) or set(entries) != set(files) | {'SOURCE-MANIFEST.json', 'README-SOURCE.txt'}:
            raise ScaffoldError("Bundle entries do not match the source manifest")
        for name, digest in files.items():
            if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
                    or hashlib.sha256(content(name)).hexdigest() != digest):
                raise ScaffoldError(f"Source manifest hash mismatch: {name}")
        upstream = [name for name in files if name.startswith('upstream/')]
        if len(upstream) != 1 or any(not n.startswith(('packaging/', 'upstream/')) for n in files):
            raise ScaffoldError("Expected one upstream archive and packaging inputs only")
        source = manifest['upstream']
        if files[upstream[0]] != source['sha256']:
            raise ScaffoldError("Upstream archive differs from manifest source pin")
        recipe_name = 'packaging/recipes/renderdem/recipe.yaml'
        if recipe_name not in files:
            raise ScaffoldError("RenderDEM recipe missing from bundle")
        text = content(recipe_name).decode('utf-8')
        stanza = f"  url: https://codeload.github.com/OpenDroneMap/RenderDEM/tar.gz/{source['commit']}\n  sha256: ${{{{ source_sha256 }}}}\n"
        if text.count(stanza) != 1 or source['sha256'] not in text:
            raise ScaffoldError("Recipe source stanza does not match the manifest")
        destination.mkdir(parents=True, exist_ok=False)
        try:
            for name in files:
                if name.startswith('packaging/'):
                    target = destination.joinpath(*PurePosixPath(name).parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content(name))
                    target.chmod(0o755 if entries[name].mode & 0o111 else 0o644)
            archive = destination / 'upstream.tar.gz'
            archive.write_bytes(content(upstream[0]))
            source_dir = (destination / 'upstream-source').resolve()
            source_dir.mkdir()
            unpack_archive(archive, source_dir)
            recipe = destination / recipe_name
            recipe.write_text(text.replace(stanza, f"  path: {json.dumps(str(source_dir))}\n"), encoding='utf-8')
        except Exception:
            shutil.rmtree(destination)
            raise
    return recipe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--sha256', required=True, help='Independently obtained full bundle SHA256')
    parser.add_argument('--destination', required=True, type=Path, help='New staging directory')
    args = parser.parse_args()
    recipe = prepare(args.bundle, args.sha256, args.destination)
    print(f'Prepared local-source recipe: {recipe}')
    print('Run rattler-build using this recipe and the staged recipes/variants.yaml; dependencies remain online.')


if __name__ == '__main__':
    fail_cli(main)
