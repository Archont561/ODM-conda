"""Recognize one exact research source graph; this is not release approval.

The Eigen lapack build tree contains a download command. The reduced OpenMVS
build uses Eigen headers only; callers may exclude that tree from static fetch
scanning *only for the exact pinned Eigen archive*. Network isolation and
source/license completeness must still be validated independently.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from common import ROOT, ScaffoldError, relative_path, sha256

OPENMVS = {
    'name': 'openmvs',
    'commit': '8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53',
    'sha256': '949d420d4506ccd0189574252c8214acce666de837e400e44682e8ddc13e666b',
    'url': 'https://codeload.github.com/OpenDroneMap/openMVS/tar.gz/8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53',
}
VCG = {
    'name': 'vcg',
    'commit': '3fe55c6fa48ca111dab31eaa594ecab33913a8f1',
    'sha256': '8f75239f9dd4ee5ba55b0cad25df1b7f9caa8a7e583f8174b40d38421b485f45',
    'url': 'https://codeload.github.com/OpenDroneMap/VCG/tar.gz/3fe55c6fa48ca111dab31eaa594ecab33913a8f1',
    'path': '_external/vcg',
}
EIGEN = {
    'name': 'eigen34',
    'commit': '7176ae16238ded7fb5ed30a7f5215825b3abd134',
    'sha256': 'a14492af4d1451a686caadbfd5047ca1216b8c66e71f0e8385afc4bb3ecdc7a3',
    'url': 'https://codeload.github.com/eigenteam/eigen-git-mirror/tar.gz/7176ae16238ded7fb5ed30a7f5215825b3abd134',
    'path': '_external/eigen',
}


# Hashes file names and bytes after applying the two documented research patches.
# Directory entries and executable modes are not part of this fingerprint.
EXPECTED_TREE = (3297, 'fe27f5deb6774cd3204f8c70914a7e9fa05c7fb4ac4e1c37d7fe782658c4c668')


def fingerprint_tree(tree: Path) -> tuple[int, str]:
    if tree.is_symlink() or not tree.is_dir():
        raise ScaffoldError('Invalid source tree')
    digest = hashlib.sha256()
    count = total = 0
    for path in sorted(tree.rglob('*')):
        if path.is_symlink():
            raise ScaffoldError(f'Source tree contains symlink: {path}')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ScaffoldError(f'Source tree contains a special file: {path}')
        count += 1
        total += path.stat().st_size
        if count > 50000 or total > 1024 * 1024 * 1024:
            raise ScaffoldError('Source tree exceeds fingerprint limits')
        name = path.relative_to(tree).as_posix().encode('utf-8')
        digest.update(len(name).to_bytes(8, 'big'))
        digest.update(name)
        digest.update(bytes.fromhex(sha256(path)))
    return count, digest.hexdigest()


def verify_openmvs_tree(tree: Path) -> None:
    if fingerprint_tree(tree) != EXPECTED_TREE:
        raise ScaffoldError('Unrecognized OpenMVS source tree fingerprint')


def validate_openmvs_patches(source: dict[str, Any], root: Path = ROOT) -> None:
    expected = [
        ('research/patches/openmvs-reconstruct-only.patch', '2dc920d550119443bb8d079911b0cdfc4cc747eb916a48a01e09ebdaf6a2c96a'),
        ('research/patches/openmvs-visibility-check.patch', '74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90'),
    ]
    patches = source.get('patches')
    if not isinstance(patches, list) or len(patches) != len(expected):
        raise ScaffoldError('Unreviewed OpenMVS patch metadata')
    for patch, (filename, digest) in zip(patches, expected):
        if (not isinstance(patch, dict) or patch.get('file') != filename or patch.get('sha256') != digest
                or not isinstance(patch.get('summary'), str) or not patch['summary'].strip()):
            raise ScaffoldError('Unreviewed OpenMVS patch metadata')
        path = relative_path(root, filename)
        if (root / filename).is_symlink() or not path.is_file() or sha256(path) != digest:
            raise ScaffoldError('OpenMVS patch checksum mismatch')


def validate_openmvs_graph(name: str, source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fail closed unless all archive bytes and staging paths match the pin."""
    primary = {key: source.get(key) for key in ('commit', 'sha256', 'url')}
    expected = {key: OPENMVS[key] for key in ('commit', 'sha256', 'url')}
    if (name != 'openmvs-odm' or primary != expected
            or source.get('additional_sources') != [VCG, EIGEN]
            or source.get('disabled_build_trees') != []):
        raise ScaffoldError('Unreviewed external source graph; do not build or bundle it')
    return dict(OPENMVS), [dict(VCG), dict(EIGEN)]
