#!/usr/bin/env python3
"""Derive a local-only asset-reduced OpenSfM runtime from an installed copy.

This is not a Conda package, source bundle, or license/release approval. The
original archives and package contain all assets; retain them privately.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import ScaffoldError, fail_cli, sha256

DATASET_SHA256 = 'b592b1c0a67390680116050a71631837e73830094c057b6fd5832332c27448b0'
EXCLUDED_ASSETS = {
    'data/bow/bow_hahog_root_uchar_10000.npz': '474a88e67ea717acf96dd5d151df7a90724e84300153a339d1fdc23ba4133b7c',
    'data/bow/bow_hahog_root_uchar_64.npz': 'e2df17d92ebfba50fcbfc934e1805e474dd4095f5ed4e1cbeae1ef1caaeb3749',
    'data/sensor_data.sqlite': '45e7b0ed2d9978ae236ae522497514ded59ffd83f76bc0180555a36b2562fa31',
}


def make_scoped_runtime(source: Path, destination: Path) -> dict:
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or not source.is_dir() or destination.exists() or destination.is_symlink():
        raise ScaffoldError('Unsafe or existing runtime source/destination')
    if not destination.parent.is_dir() or source.resolve().is_relative_to(destination.resolve()) or destination.resolve().is_relative_to(source.resolve()):
        raise ScaffoldError('Runtime paths must not overlap and destination parent must exist')
    if any(path.is_symlink() or not (path.is_file() or path.is_dir()) for path in source.rglob('*')):
        raise ScaffoldError('Runtime source has a symlink or special file')
    dataset = source / 'dataset.py'
    if not dataset.is_file() or sha256(dataset) != DATASET_SHA256:
        raise ScaffoldError('Unexpected installed OpenSfM dataset module')
    for name, expected in EXCLUDED_ASSETS.items():
        path = source / name
        if not path.is_file() or sha256(path) != expected:
            raise ScaffoldError(f'Unexpected or missing OpenSfM asset: {name}')
    marker = '\n    def _image_list_file(self)'
    text = dataset.read_text(encoding='utf-8')
    if text.count(marker) != 1 or (source / 'scoped_runtime_guard.py').exists():
        raise ScaffoldError('Unexpected OpenSfM dataset structure')
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise ScaffoldError('Unsafe or existing runtime destination') from error
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        for name in EXCLUDED_ASSETS:
            (destination / name).unlink()
        guard = Path(__file__).with_name('opensfm_scoped_guard.py')
        shutil.copyfile(guard, destination / 'scoped_runtime_guard.py')
        injection = '\n        from opensfm.scoped_runtime_guard import validate_config\n        validate_config(self.config)\n'
        modified = text.replace(marker, injection + marker)
        compile(modified, str(destination / 'dataset.py'), 'exec')
        (destination / 'dataset.py').write_text(modified, encoding='utf-8')
        return {'scope': 'local-research-only', 'excluded_count': len(EXCLUDED_ASSETS),
                'excluded_assets': EXCLUDED_ASSETS, 'dataset_sha256': sha256(destination / 'dataset.py'),
                'guard_sha256': sha256(destination / 'scoped_runtime_guard.py')}
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Installed opensfm package directory')
    parser.add_argument('--destination', type=Path, required=True, help='New local-only opensfm directory')
    args = parser.parse_args()
    print(json.dumps(make_scoped_runtime(args.source, args.destination), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
