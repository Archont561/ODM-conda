"""Prepare a non-distributable, local-only OpenMVS research tree.

This copies from the verified patched source graph and omits specific files. It
is not a corresponding-source offer, license clearance, or an archive builder.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from common import ScaffoldError, fail_cli, sha256
from openmvs_graph_policy import fingerprint_tree, verify_openmvs_tree

EXPECTED_REDUCED_TREE = (3274, 'e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489')
OMIT_DIRS = ('libs/Math/IBFS', 'libs/Math/TRWS')
OMIT_FILES = ('libs/MVS/SceneDensify.cpp', 'libs/MVS/SceneRefine.cpp', 'libs/MVS/SceneTexture.cpp')
GENERATED = frozenset({'.source_info.json', 'build_env.sh', 'conda_build.sh', 'conda_build.log'})
NOTICES = ('LICENSE', 'COPYRIGHT.md', '_external/vcg/LICENSE.txt',
           '_external/eigen/COPYING.MPL2', '_external/eigen/COPYING.README')


def make_reduced_tree(source: Path, destination: Path) -> dict:
    """Copy the exact patched graph minus named paths, returning a stable manifest.

    Destination must not exist or overlap source. Failure removes only the newly
    created destination. The original source must stay available to the caller.
    """
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or destination.is_symlink() or destination.exists():
        raise ScaffoldError('Unsafe or existing source/destination')
    resolved_source, resolved_dest = source.resolve(), destination.resolve()
    if resolved_dest.is_relative_to(resolved_source) or resolved_source.is_relative_to(resolved_dest):
        raise ScaffoldError('Source and destination must not overlap')
    if not destination.parent.is_dir():
        raise ScaffoldError('Destination parent is missing')
    verify_openmvs_tree(source, research=True)
    for name in OMIT_DIRS:
        path = source / name
        if path.is_symlink() or not path.is_dir():
            raise ScaffoldError(f'Missing or unsafe omitted directory: {name}')
    for name in OMIT_FILES + NOTICES:
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ScaffoldError(f'Missing or unsafe input: {name}')
    count = sum(1 for name in OMIT_DIRS for p in (source / name).rglob('*') if p.is_file())
    if count != 20:
        raise ScaffoldError('Unexpected restricted-directory file count')
    destination.mkdir()
    try:
        files = {}
        for path in sorted(source.rglob('*')):
            rel = path.relative_to(source)
            name = rel.as_posix()
            if path.is_symlink():
                raise ScaffoldError(f'Symlink in source tree: {name}')
            if (any(name == directory or name.startswith(directory + '/') for directory in OMIT_DIRS)
                    or name in OMIT_FILES or (len(rel.parts) == 1 and name in GENERATED)):
                continue
            if path.is_dir():
                continue
            if not path.is_file():
                raise ScaffoldError(f'Special file in source tree: {name}')
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            mode = path.stat().st_mode & 0o777
            os.chmod(target, mode)
            files[name] = {'sha256': sha256(target), 'mode': f'{mode:04o}'}
        count, digest = fingerprint_tree(destination)
        if EXPECTED_REDUCED_TREE is not None and (count, digest) != EXPECTED_REDUCED_TREE:
            raise ScaffoldError('Unexpected reduced source fingerprint')
        return {'scope': 'local-research-only', 'retained_count': count,
                'tree_sha256': digest, 'omitted_directories': list(OMIT_DIRS),
                'omitted_files': list(OMIT_FILES), 'files': files}
    except Exception:
        shutil.rmtree(destination)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Exact patched and staged local research tree')
    parser.add_argument('--destination', type=Path, required=True, help='New local-only output directory')
    args = parser.parse_args()
    print(json.dumps(make_reduced_tree(args.source, args.destination), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
