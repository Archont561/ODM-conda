"""Recognize one exact texturing source graph; not a license approval.

The listed CMake fetch sites are unused by the proposed patched build.  The
exceptions only identify exact original file contents; callers must also
validate patched build behavior and network isolation before publication.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import ROOT, ScaffoldError, relative_path, sha256
from openmvs_graph_policy import fingerprint_tree

PRIMARY = {'name': 'texturing',
 'commit': 'c5a4d0c9a434553533c6e39d426e349fcfa5f48d',
 'sha256': '295b11cb35c85f44908294bc89cd7d4f1057dee0016cc4cd35a5ed01570766f8',
 'url': 'https://codeload.github.com/OpenDroneMap/mvs-texturing/tar.gz/c5a4d0c9a434553533c6e39d426e349fcfa5f48d'}

ADDITIONAL = [{'name': 'mve',
  'commit': '90f13c18f92db6089c06c8c2451e283911f5f634',
  'sha256': 'f4d0d76a925d7482d14c2050b4488718c824947a3895eac196eac70ef19fc699',
  'url': 'https://codeload.github.com/OpenDroneMap/mve/tar.gz/90f13c18f92db6089c06c8c2451e283911f5f634',
  'path': '_external/mve'},
 {'name': 'mapmap',
  'commit': 'fa526e0963ca3e431a02aa7b9e87b85ba8a8e304',
  'sha256': '01ab05c7f7e6e14f5a54bc2111f6af382b148a504670a30b42b70b1851767e39',
  'url': 'https://codeload.github.com/dthuerck/mapmap_cpu/tar.gz/fa526e0963ca3e431a02aa7b9e87b85ba8a8e304',
  'path': 'elibs/mapmap'},
 {'name': 'rayint',
  'commit': 'ad9f826a8b134090511709e5813a8ba56dc2e837',
  'sha256': '7ed6d0af9ba58cb359eaed25bd87fa818507abe41fe56cf7ff9929dd953212a7',
  'url': 'https://codeload.github.com/pierotofy/rayint/tar.gz/ad9f826a8b134090511709e5813a8ba56dc2e837',
  'path': 'elibs/rayint'},
 {'name': 'eigen332',
  'commit': '477d1e81928a8514d2cca6a6e1e7e478eecd8634',
  'sha256': '8e473e564dcbee29154cdcf6a1ddba32863751a68f17cdb0ec49193488178960',
  'url': 'https://codeload.github.com/eigenteam/eigen-git-mirror/tar.gz/477d1e81928a8514d2cca6a6e1e7e478eecd8634',
  'path': 'elibs/eigen'}]

FETCH_EXCEPTIONS = {'texturing': {'elibs/CMakeLists.txt': '0873544958710fd22f4f7f4c352e03f7b73bce793709fdcf90386260b4b391f9'},
 'mve': {},
 'mapmap': {'CMakeLists.txt': '1d08c4aceeda399da2f3a455beb46f0834b1884e57b7d49d9395ea8e42d9314f',
            'download_example/CMakeLists.txt': 'ace17c6a35d223f5dc22ded308786682f9ee2dd3677d13b55d5a6cbc0ffd456a'},
 'rayint': {'elibs/CMakeLists.txt': '585ef9bb53d3461abb71a55d6c81e314e4d2b8b2a6365c35031c68e55fd8dc3d'},
 'eigen332': {'lapack/CMakeLists.txt': '73e35ab3b44d843dc4512543b92826134e26546825faf60b4afa52f074c2cd30'}}

EXPECTED_TREE = (2227, '21fbdd907821e713478834d4c5e89d40e58787633880086e32b2a9c51b2d8c3e')


def verify_texturing_tree(tree: Path) -> None:
    metadata = tree / '.source_info.json'
    ignored = frozenset()
    if metadata.is_symlink():
        raise ScaffoldError('Source metadata is a symlink')
    if metadata.exists():
        if not metadata.is_file() or metadata.stat().st_size > 1024 * 1024:
            raise ScaffoldError('Invalid rattler source metadata')
        try:
            recorded = json.loads(metadata.read_text(encoding='utf-8'))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ScaffoldError('Invalid rattler source metadata') from error
        expected = [{'url': PRIMARY['url'], 'sha256': PRIMARY['sha256'], 'patches': ['patches/0001-offline.patch']}]
        for entry in ADDITIONAL:
            item = {'url': entry['url'], 'sha256': entry['sha256'], 'target_directory': entry['path']}
            if entry['name'] == 'mve':
                item['patches'] = ['patches/0002-mve-baseline.patch']
            expected.append(item)
        if not isinstance(recorded, dict) or recorded.get('sources') != expected:
            raise ScaffoldError('Unrecognized rattler source metadata')
        # Rattler-build 0.68 creates these root files immediately before running
        # the recipe. They are not upstream sources and contain variable build
        # paths/log output. Do not extend this exception to other files or trees.
        generated = frozenset({'build_env.sh', 'conda_build.sh', 'conda_build.log'})
        for name in generated:
            path = tree / name
            if path.is_symlink():
                raise ScaffoldError(f'Rattler generated file is a symlink: {path}')
            if path.exists() and not path.is_file():
                raise ScaffoldError(f'Invalid rattler generated file: {path}')
        ignored = generated | {'.source_info.json'}
    if fingerprint_tree(tree, ignore_root_files=ignored) != EXPECTED_TREE:
        raise ScaffoldError('Unrecognized texturing source tree fingerprint')


def validate_texturing_patches(source: dict[str, Any], root: Path = ROOT) -> None:
    expected = [
        ('research/patches/mvs-texturing-offline.patch', '37d03ca8b5a50bd72b6e7a4ed2f2856e1d83c0355806f7fc9efa059f9a57ef65', '.'),
        ('research/patches/mve-baseline-cpu.patch', '7427f3332ba65a1ebf677940fbf9ec957c7343a311844953d829d30e0944646c', '_external/mve'),
    ]
    patches = source.get('patches')
    if not isinstance(patches, list) or len(patches) != len(expected):
        raise ScaffoldError('Unreviewed texturing patch metadata')
    for patch, (filename, digest, target) in zip(patches, expected):
        if (not isinstance(patch, dict) or patch.get('file') != filename or patch.get('sha256') != digest or patch.get('target') != target
                or not isinstance(patch.get('summary'), str) or not patch['summary'].strip()):
            raise ScaffoldError('Unreviewed texturing patch metadata')
        path = relative_path(root, filename)
        if (root / filename).is_symlink() or not path.is_file() or sha256(path) != digest:
            raise ScaffoldError('Texturing patch checksum mismatch')


def validate_texturing_graph(name: str, source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fail closed unless source archives and staging locations match exactly."""
    primary = {key: source.get(key) for key in ('commit', 'sha256', 'url')}
    expected = {key: PRIMARY[key] for key in ('commit', 'sha256', 'url')}
    if (name != 'mvs-texturing-odm' or primary != expected
            or source.get('additional_sources') != ADDITIONAL
            or source.get('disabled_build_trees') != []):
        raise ScaffoldError('Unreviewed external source graph; do not build or bundle it')
    return dict(PRIMARY), [dict(entry) for entry in ADDITIONAL]
