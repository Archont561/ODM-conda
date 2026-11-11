#!/usr/bin/env python3
"""Stage bounded private TetraFlow research inputs; not a source offer or release bundle.

Archives are caller-supplied and hash-pinned. This deliberately excludes Conda
binary dependencies, build/host source closure, tools, and a final replay lock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tarfile
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True  # Verification must not modify a relocated receipt.
from common import ROOT, ScaffoldError, fail_cli, sha256

ARCHIVES = {
    'openmvs.tar.gz': ('4701b4490c8036bc548f23b949d871bd2c133386051aad051d1f3de912b26014',
                       'openMVS-0aebb63a7dc72f2831615b441fdf2f474d7a0ea0'),
    'eigen.tar.gz': ('a14492af4d1451a686caadbfd5047ca1216b8c66e71f0e8385afc4bb3ecdc7a3',
                     'eigen-git-mirror-7176ae16238ded7fb5ed30a7f5215825b3abd134'),
}
INPUTS = (
    'LICENSE', 'recipes/variants.yaml', 'scripts/tetraflow_source_receipt.py',
    'tests/test_tetraflow_source_receipt.py',
    'research/recipes/openmvs-tetraflow-research/recipe.yaml',
    'research/recipes/openmvs-tetraflow-research/patches/visibility-ply.patch',
    'scripts/build_openmvs_tetraflow_research.py', 'scripts/common.py', 'scripts/openmvs_link_map.py',
    'scripts/openmvs_synthetic_fixture.py', 'scripts/openmvs_pointcloud_fixture.py',
    'scripts/openmvs_fixture.py', 'scripts/texrecon_fixture.py',
    'scripts/openmvs_tetraflow_weights_fixture.py', 'scripts/openmvs_odm_cleanup_fixture.py',
)
SCOPE = ('private-research-input-receipt; incomplete: no Conda dependency or toolchain source, '
         'release lock, legal clearance, source offer, or approval')


def inspect_archive(path: Path, expected_digest: str, root_name: str) -> dict:
    if path.is_symlink() or not path.is_file() or sha256(path) != expected_digest:
        raise ScaffoldError('Missing, unsafe or mismatched pinned archive')
    files = {}
    seen = set()
    total = 0
    try:
        with tarfile.open(path, 'r:gz') as archive:
            for member in archive:
                name = member.name
                parts = PurePosixPath(name).parts
                if (not name or name.startswith('/') or '\\' in name or '..' in parts or
                        not parts or parts[0] != root_name or name in seen):
                    raise ScaffoldError(f'Unsafe or duplicate archive path: {name}')
                seen.add(name)
                if len(seen) > 50000:
                    raise ScaffoldError('Archive member limit exceeded')
                if member.isdir():
                    continue
                if not member.isfile() or member.size < 0:
                    raise ScaffoldError(f'Unsupported archive entry: {name}')
                total += member.size
                if total > 1024 * 1024 * 1024 or member.size > 128 * 1024 * 1024:
                    raise ScaffoldError('Archive size limit exceeded')
                if len(parts) < 2:
                    raise ScaffoldError('Unexpected archive root file')
                stream = archive.extractfile(member)
                if stream is None:
                    raise ScaffoldError(f'Cannot read archive member: {name}')
                digest = hashlib.sha256()
                while block := stream.read(1024 * 1024):
                    digest.update(block)
                relative = '/'.join(parts[1:])
                if relative in files:
                    raise ScaffoldError(f'Duplicate archive file: {relative}')
                files[relative] = {'sha256': digest.hexdigest(), 'size': member.size}
    except (tarfile.TarError, OSError, EOFError) as error:
        raise ScaffoldError(f'Invalid source archive: {error}') from error
    if not files:
        raise ScaffoldError('Empty source archive')
    notices = [name for name in files if any(word in PurePosixPath(name).name.lower()
               for word in ('license', 'licence', 'copyright', 'copying', 'notice'))]
    return {'sha256': expected_digest, 'file_count': len(files), 'bytes': total,
            'files': dict(sorted(files.items())), 'notice_name_candidates': sorted(notices)}


def stage(openmvs: Path, eigen: Path, destination: Path, *, root: Path = ROOT) -> str:
    destination, root = Path(destination), Path(root).resolve()
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise ScaffoldError('Destination must be new with an existing parent')
    resolved = destination.resolve()
    if resolved.is_relative_to(root) or root.is_relative_to(resolved):
        raise ScaffoldError('Private destination must not overlap the repository')
    archives = {'openmvs.tar.gz': Path(openmvs), 'eigen.tar.gz': Path(eigen)}
    records = {name: inspect_archive(path, *ARCHIVES[name]) for name, path in archives.items()}
    for name in ('libs/Math/IBFS', 'libs/Math/TRWS'):
        if any(p == name or p.startswith(name + '/') for p in records['openmvs.tar.gz']['files']):
            raise ScaffoldError(f'Restricted directory present: {name}')
    for name in INPUTS:
        file = root / name
        if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root):
            raise ScaffoldError(f'Missing or unsafe packaging input: {name}')
    destination.mkdir(mode=0o700)
    try:
        copied = {}
        for name, path in archives.items():
            target = destination / 'archives' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            if sha256(target) != ARCHIVES[name][0]:
                raise ScaffoldError('Archive changed during copying')
            copied[f'archives/{name}'] = sha256(target)
        for name in INPUTS:
            target = destination / 'packaging' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
            copied[f'packaging/{name}'] = sha256(target)
        manifest = {'schema_version': 1, 'scope': SCOPE, 'archives': records,
                    'receipt_files': dict(sorted(copied.items()))}
        out = destination / 'receipt.json'
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        return sha256(out)
    except Exception:
        shutil.rmtree(destination)
        raise



def verify(destination: Path, expected_sha256: str) -> dict:
    destination = Path(destination)
    manifest = destination / 'receipt.json'
    if (not re.fullmatch(r'[0-9a-f]{64}', expected_sha256) or destination.is_symlink()
            or not destination.is_dir() or manifest.is_symlink() or not manifest.is_file()
            or manifest.stat().st_size > 8 * 1024 * 1024 or sha256(manifest) != expected_sha256):
        raise ScaffoldError('Missing, unsafe or mismatched receipt manifest')
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ScaffoldError(f'Invalid receipt manifest: {error}') from error
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('scope') != SCOPE:
        raise ScaffoldError('Unexpected receipt scope')
    expected_names = {f'archives/{name}' for name in ARCHIVES} | {f'packaging/{name}' for name in INPUTS}
    files = data.get('receipt_files')
    if not isinstance(files, dict) or set(files) != expected_names:
        raise ScaffoldError('Unexpected receipt file list')
    found = set()
    for path in destination.rglob('*'):
        if path.is_symlink():
            raise ScaffoldError('Receipt contains a symlink')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ScaffoldError('Receipt contains a special file')
        found.add(path.relative_to(destination).as_posix())
    if found != expected_names | {'receipt.json'}:
        raise ScaffoldError('Unexpected or missing receipt file')
    for name, digest in files.items():
        if not isinstance(digest, str) or sha256(destination / name) != digest:
            raise ScaffoldError(f'Receipt file checksum mismatch: {name}')
    recorded = data.get('archives')
    if not isinstance(recorded, dict) or set(recorded) != set(ARCHIVES):
        raise ScaffoldError('Unexpected archive records')
    for name, (digest, root_name) in ARCHIVES.items():
        if inspect_archive(destination / 'archives' / name, digest, root_name) != recorded[name]:
            raise ScaffoldError(f'Archive inventory mismatch: {name}')
    return data

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    create = sub.add_parser('stage')
    create.add_argument('--openmvs', required=True, type=Path)
    create.add_argument('--eigen', required=True, type=Path)
    create.add_argument('--destination', required=True, type=Path)
    check = sub.add_parser('verify')
    check.add_argument('--receipt', required=True, type=Path)
    check.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    if args.action == 'stage':
        digest = stage(args.openmvs, args.eigen, args.destination)
        print(f'Private incomplete input receipt created; independently record receipt SHA256: {digest}')
    else:
        data = verify(args.receipt, args.manifest_sha256)
        print(f"PASS: private incomplete input receipt and {len(data['receipt_files'])} files verified; no rights conclusion")


if __name__ == '__main__':
    fail_cli(main)
