#!/usr/bin/env python3
"""Make a private deterministic OpenSfM source candidate; not a source offer."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

from common import ScaffoldError, fail_cli, sha256
from opensfm_scoped_runtime import EXCLUDED_ASSETS
from source_bundle import add_bytes
from source_graph import unpack_archive

PINNED_SHA256 = '2bd9ec9ed20c5b426ff2808734e0a8849e2375038e378105f97128e48d704f8e'


def make_candidate(source: Path, destination: Path) -> dict:
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or not source.is_file() or sha256(source) != PINNED_SHA256:
        raise ScaffoldError('Unexpected OpenSfM source archive')
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise ScaffoldError('Unsafe or existing destination')
    with tempfile.TemporaryDirectory(prefix='opensfm-source-', dir=destination.parent) as temp:
        tree = Path(temp) / 'tree'
        tree.mkdir()
        unpack_archive(source, tree)
        excluded = {'opensfm/' + path: digest for path, digest in EXCLUDED_ASSETS.items()}
        for name, expected in excluded.items():
            path = tree / name
            if path.is_symlink() or not path.is_file() or sha256(path) != expected:
                raise ScaffoldError(f'Unexpected asset: {name}')
            path.unlink()
        files = {}
        for path in sorted(tree.rglob('*')):
            if path.is_symlink() or not (path.is_dir() or path.is_file()):
                raise ScaffoldError('Unsupported source member')
            if path.is_file():
                files[path.relative_to(tree).as_posix()] = {'sha256': sha256(path), 'mode': f'{path.stat().st_mode & 0o777:04o}'}
        if 'CANDIDATE-MANIFEST.json' in files:
            raise ScaffoldError('Unexpected manifest in source')
        manifest = {'scope': 'local-research-only', 'original_archive_sha256': PINNED_SHA256,
                    'excluded_files': excluded, 'files': files,
                    'warning': 'Original archives, additional sources, runtime guard, dependency sources, notices and rights remain unreviewed. Not corresponding source.'}
        try:
            output = destination.open('xb')
        except FileExistsError as error:
            raise ScaffoldError('Unsafe or existing destination') from error
        try:
            with output, gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
                    for name, info in files.items():
                        add_bytes(archive, 'source/' + name, (tree / name).read_bytes(), int(info['mode'], 8))
                    add_bytes(archive, 'source/CANDIDATE-MANIFEST.json', (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = make_candidate(args.source, args.output)
    print(f"Private candidate: {sha256(args.output)}; {len(manifest['files'])} files; {len(manifest['excluded_files'])} omitted")


if __name__ == '__main__':
    fail_cli(main)
