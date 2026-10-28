#!/usr/bin/env python3
"""Check pinned OpenSfM runtime assets; this is not legal or dataset validation."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

# Files explicitly installed by the pinned upstream setup.py. Hashes identify
# bytes only; in particular they do not resolve vocabulary training-data rights.
ASSETS = {
    'data/bow/bow_hahog_root_uchar_10000.npz': '474a88e67ea717acf96dd5d151df7a90724e84300153a339d1fdc23ba4133b7c',
    'data/bow/bow_hahog_root_uchar_64.npz': 'e2df17d92ebfba50fcbfc934e1805e474dd4095f5ed4e1cbeae1ef1caaeb3749',
    'data/sensor_data.json': 'ecc564167bb1e7f01648094a5a9a1a3f43d7b00b3bd9afa0afca2913fd2620d8',
    'data/camera_calibration.yaml': '98cce9327b2d00edd77bfa227b0c0ded436003b92d76a9b035b7a29060c1321a',
}


def verify_assets(root: Path) -> None:
    """Check a source root or site-packages directory containing opensfm/."""
    for relative, expected in ASSETS.items():
        path = root / 'opensfm' / relative
        current = root
        for part in ('opensfm', *Path(relative).parts):
            current = current / part
            if current.is_symlink():
                raise ValueError(f'OpenSfM asset path contains symlink: {current}')
        if not path.is_file():
            raise ValueError(f'OpenSfM asset missing: {path}')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise ValueError(f'OpenSfM asset checksum mismatch: {path}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='source root or site-packages directory containing opensfm/')
    args = parser.parse_args()
    try:
        verify_assets(args.root)
    except (OSError, ValueError) as error:
        parser.exit(1, f'ERROR: {error}\n')
    print('PASS: pinned OpenSfM runtime assets; no license or dataset validation implied')


if __name__ == '__main__':
    main()
