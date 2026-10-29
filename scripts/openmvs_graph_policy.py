"""Recognize one exact research source graph; this is not release approval.

The Eigen lapack build tree contains a download command. The reduced OpenMVS
build uses Eigen headers only; callers may exclude that tree from static fetch
scanning *only for the exact pinned Eigen archive*. Network isolation and
source/license completeness must still be validated independently.
"""
from __future__ import annotations

import hashlib
import json
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


# Hashes file names and bytes after the respective production or research patches.
# Directory entries and executable modes are not part of this fingerprint.
EXPECTED_TREE = (3297, '4d37a931d8ac36a757007ef68661f8e362a2b9372e6916c1ad628b92ea2f558a')
RESEARCH_EXPECTED_TREE = (3297, '25a71e02cecf70460d78543c104d8d14e9c5b65456183e96c1674d696f60d217')


def fingerprint_tree(tree: Path, *, ignore_root_files: frozenset[str] = frozenset()) -> tuple[int, str]:
    if tree.is_symlink() or not tree.is_dir():
        raise ScaffoldError('Invalid source tree')
    digest = hashlib.sha256()
    count = total = 0
    for path in sorted(tree.rglob('*')):
        if path.is_symlink():
            raise ScaffoldError(f'Source tree contains symlink: {path}')
        if path.parent == tree and path.name in ignore_root_files and path.is_file():
            continue
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


def rattler_generated_files(tree: Path, expected: list[dict[str, Any]], component: str) -> frozenset[str]:
    """Ignore only rattler 0.68 work files accompanied by exact source metadata."""
    metadata = tree / '.source_info.json'
    ignored = frozenset()
    if metadata.is_symlink():
        raise ScaffoldError(f'{component} source metadata is a symlink')
    if metadata.exists():
        if not metadata.is_file() or metadata.stat().st_size > 1024 * 1024:
            raise ScaffoldError(f'Invalid {component} rattler source metadata')
        try:
            recorded = json.loads(metadata.read_text(encoding='utf-8'))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ScaffoldError(f'Invalid {component} rattler source metadata') from error
        if not isinstance(recorded, dict) or recorded.get('sources') != expected:
            raise ScaffoldError(f'Unrecognized {component} rattler source metadata')
        generated = frozenset({'build_env.sh', 'conda_build.sh', 'conda_build.log'})
        for name in generated:
            path = tree / name
            if path.is_symlink():
                raise ScaffoldError(f'Rattler generated file is a symlink: {path}')
            if path.exists() and not path.is_file():
                raise ScaffoldError(f'Invalid rattler generated file: {path}')
        ignored = generated | {'.source_info.json'}
    return ignored


def verify_openmvs_tree(tree: Path, *, research: bool = False) -> None:
    expected = [
        {'url': OPENMVS['url'], 'sha256': OPENMVS['sha256'],
         'patches': ['patches/0001-reconstruct-only.patch', 'patches/0002-visibility-check.patch',
                     'patches/0003-boost-header-only-system.patch'] +
                    (['patches/0004-ply-view-indices.patch'] if research else [])},
        *[{'url': item['url'], 'sha256': item['sha256'], 'target_directory': item['path']}
          for item in (VCG, EIGEN)],
    ]
    ignored = rattler_generated_files(tree, expected, 'OpenMVS')
    if fingerprint_tree(tree, ignore_root_files=ignored) != (RESEARCH_EXPECTED_TREE if research else EXPECTED_TREE):
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
