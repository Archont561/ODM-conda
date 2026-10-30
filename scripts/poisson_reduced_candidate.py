#!/usr/bin/env python3
"""Create a local-only reduced Poisson source candidate, not a release bundle."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, repository_files, sha256
from source_bundle import add_bytes
from source_graph import unpack_archive

PINNED_SHA256 = '88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b'


def make_candidate(source: Path, destination: Path, root: Path = ROOT) -> dict:
    """Hash-verify and unpack original, omit JPEG, record packaging and file hashes.

    The input archive remains private and is not included in the candidate.
    This does not verify legal rights, dependency sources, or source completeness.
    """
    source, destination, root = Path(source), Path(destination), Path(root)
    if destination.exists() or destination.is_symlink():
        raise ScaffoldError('Unsafe or existing destination')
    if source.is_symlink() or not source.is_file() or sha256(source) != PINNED_SHA256:
        raise ScaffoldError('Pinned Poisson source checksum mismatch')
    if not destination.parent.is_dir() or destination.resolve().is_relative_to(root.resolve()):
        raise ScaffoldError('Candidate destination must be outside the packaging tree')
    with tempfile.TemporaryDirectory(prefix='poisson-candidate-', dir=destination.parent) as temporary:
        tree = Path(temporary) / 'tree'
        tree.mkdir()
        unpack_archive(source, tree)
        jpeg = tree / 'JPEG'
        if jpeg.is_symlink() or not jpeg.is_dir():
            raise ScaffoldError('Missing vendored JPEG directory')
        excluded = sorted(jpeg.rglob('*'))
        if len(excluded) != 59 or any(p.is_symlink() or not p.is_file() for p in excluded):
            raise ScaffoldError('Unexpected vendored JPEG contents')
        excluded_hashes = {p.relative_to(tree).as_posix(): sha256(p) for p in excluded}
        entries = {}
        for path in sorted(tree.rglob('*')):
            if path.is_symlink():
                raise ScaffoldError('Symlink in staged source')
            if path.is_file() and not path.is_relative_to(jpeg):
                entries['source/' + path.relative_to(tree).as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
        # The broad packaging allowlist contains upstream-derived JPEG comparison
        # text in research/. This focused candidate omits research material.
        for path in repository_files(root):
            relative = path.relative_to(root)
            if relative.parts[0] == 'research' or path.name.startswith('tmp-'):
                continue
            entries['packaging/' + relative.as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
        manifest = {'schema_version': 1, 'scope': 'local-research-only', 'original_archive_sha256': PINNED_SHA256,
                    'excluded_file_count': len(excluded_hashes), 'excluded_files': excluded_hashes,
                    'files': {name: hashlib.sha256(data).hexdigest() for name, (data, _) in sorted(entries.items())},
                    'warning': 'Not a corresponding-source offer or license clearance. Patches still need to be applied.'}
        entries['CANDIDATE-MANIFEST.json'] = ((json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode(), 0o644)
        try:
            with destination.open('xb') as output, gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
                    directory = tarfile.TarInfo('source/JPEG')
                    directory.type = tarfile.DIRTYPE
                    directory.mode = 0o755
                    directory.mtime = directory.uid = directory.gid = 0
                    archive.addfile(directory)
                    for name, (data, mode) in sorted(entries.items()):
                        add_bytes(archive, name, data, mode)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = make_candidate(args.source, args.output)
    print(f"Local-only candidate: {args.output}; SHA256 {sha256(args.output)}; excluded {result['excluded_file_count']} JPEG files")


if __name__ == '__main__':
    fail_cli(main)
