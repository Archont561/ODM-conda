#!/usr/bin/env python3
"""Create a private JPEG XL vendor-scope trial, not a source offer or release.

Only the exact locked jpegxl-src crate may be trimmed. Retained and removed
files are recorded against the independently hash-verified crate archive.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from source_bundle import add_bytes
from source_graph import unpack_archive

CRATE = 'jpegxl-src-0.11.2'
CRATE_SHA256 = '96c328aa9d824459bfb9aef47b8b3defa126df1bbd6fd3a1e59e703911d6dd00'
REMOVED_PREFIX = 'libjxl/'
REMOVED_COUNT = 1488
RETAINED_COUNT = 8
CARGO_OMITTED = {
    'libjxl/.gitignore', 'libjxl/third_party/brotli/.gitattributes',
    'libjxl/third_party/brotli/.gitignore', 'libjxl/third_party/highway/.gitignore',
    'libjxl/third_party/highway/docs/.gitignore', 'libjxl/third_party/skcms/.gitignore',
    'libjxl/third_party/zlib/.gitignore', 'libjxl/tools/fast_lossless/.gitignore',
}


def files(root: Path) -> dict[str, str]:
    result = {}
    if root.is_symlink() or not root.is_dir():
        raise ScaffoldError('Expected a regular source directory')
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ScaffoldError(f'Unsafe source member: {path}')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def prepare(prepared: Path, crate_archive: Path, destination: Path) -> dict:
    prepared, crate_archive, destination = map(Path, (prepared, crate_archive, destination))
    if (destination.exists() or destination.is_symlink() or not destination.parent.is_dir()
            or destination.resolve().is_relative_to(ROOT) or destination.resolve().is_relative_to(prepared.resolve())):
        raise ScaffoldError('Unsafe or existing destination')
    if crate_archive.is_symlink() or not crate_archive.is_file() or sha256(crate_archive) != CRATE_SHA256:
        raise ScaffoldError('Unexpected original jpegxl-src crate archive')
    if set(p.name for p in prepared.iterdir()) != {'source', 'recipe'}:
        raise ScaffoldError('Unexpected prepared tree')
    files(prepared)  # reject links and special files before copying
    source = prepared/'source'; vendor = source/'vendor'/CRATE
    checksum = vendor/'.cargo-checksum.json'
    if checksum.is_symlink() or not checksum.is_file():
        raise ScaffoldError('Missing Cargo checksum metadata')
    metadata = json.loads(checksum.read_text())
    if (not isinstance(metadata, dict) or set(metadata) - {'files', 'package', '$comment'}
            or not isinstance(metadata.get('files'), dict) or metadata.get('package') != CRATE_SHA256
            or ('$comment' in metadata and not isinstance(metadata['$comment'], str))):
        raise ScaffoldError('Unexpected Cargo package checksum')
    with tempfile.TemporaryDirectory(prefix='jxl-vendor-original-', dir=destination.parent) as temp:
        original = Path(temp)/'crate'; original.mkdir()
        unpack_archive(crate_archive, original)
        archived = files(original)
        if not CARGO_OMITTED <= archived.keys():
            raise ScaffoldError('Unexpected Cargo-omitted file set')
        expected = {k:v for k,v in archived.items() if k not in CARGO_OMITTED}
        actual = files(vendor)
        actual.pop('.cargo-checksum.json', None)
        if actual != expected or metadata['files'] != expected:
            raise ScaffoldError('Vendor crate does not match the pinned original archive')
        removed = {k:v for k,v in expected.items() if k.startswith(REMOVED_PREFIX)}
        retained = {k:v for k,v in expected.items() if not k.startswith(REMOVED_PREFIX)}
        if len(removed) != REMOVED_COUNT or len(retained) != RETAINED_COUNT or 'LICENSE' not in retained:
            raise ScaffoldError('Unexpected trimmed or retained crate file set')
        original_checksum = sha256(checksum)
        try:
            destination.mkdir(mode=0o700)
        except FileExistsError as error:
            raise ScaffoldError('Unsafe or existing destination') from error
        try:
            shutil.copytree(source, destination/'source')
            shutil.copytree(prepared/'recipe', destination/'recipe')
            target = destination/'source/vendor'/CRATE
            shutil.rmtree(target/'libjxl')
            new_checksum = {**metadata, 'files': retained}
            (target/'.cargo-checksum.json').write_text(json.dumps(new_checksum, sort_keys=True, separators=(',', ':'))+'\n')
            recipe = destination/'recipe/recipe.yaml'; text = recipe.read_text()
            old = 'source:\n  path: '+json.dumps(str(source.resolve()))+'\n'
            identity = 'build:\n  number: 2\n  string: research_reduced_${{ hash }}_2\n'
            if text.count(old) != 1 or text.count(identity) != 1:
                raise ScaffoldError('Unexpected prepared recipe or source path')
            text = text.replace(old, 'source:\n  path: ../source\n')
            text = text.replace(identity, 'build:\n  number: 3\n  string: research_vendor_scope_${{ hash }}_3\n')
            recipe.write_text(text)
            manifest = {'scope': 'local-research-only', 'original_crate': CRATE,
                        'original_archive_sha256': CRATE_SHA256,
                        'original_vendor_checksum_sha256': original_checksum,
                        'modified_vendor_checksum_sha256': sha256(target/'.cargo-checksum.json'),
                        'retained': retained, 'removed': removed,
                        'cargo_omitted_from_archive': {k: archived[k] for k in sorted(CARGO_OMITTED)},
                        'warning': 'Modified crate is not the original; not a corresponding-source offer or release approval.'}
            (destination/'VENDOR-SCOPE-MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
            return manifest
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            raise


def archive(prepared: Path, destination: Path) -> None:
    prepared, destination = Path(prepared), Path(destination)
    if (destination.exists() or destination.is_symlink() or not destination.parent.is_dir()
            or destination.resolve().is_relative_to(ROOT) or destination.resolve().is_relative_to(prepared.resolve())):
        raise ScaffoldError('Unsafe or existing archive destination')
    inventory = files(prepared)
    if 'VENDOR-SCOPE-MANIFEST.json' not in inventory:
        raise ScaffoldError('Missing vendor scope manifest')
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise ScaffoldError('Unsafe or existing archive destination') from error
    try:
        with os.fdopen(fd, 'wb') as output, gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as tar:
                for name in inventory:
                    path=prepared/name
                    add_bytes(tar, 'research/'+name, path.read_bytes(), path.stat().st_mode & 0o777)
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--crate', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    result=prepare(args.prepared, args.crate, args.destination)
    archive(args.destination, args.archive)
    print(f"Private research archive {sha256(args.archive)}; removed {len(result['removed'])} files; not a source offer")


if __name__ == '__main__':
    fail_cli(main)
