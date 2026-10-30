#!/usr/bin/env python3
"""Installed scoped OpenSfM behavior; no license or dataset clearance."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site_packages', type=Path)
    args = parser.parse_args()
    package = args.site_packages / 'opensfm'
    for rel in ('data/sensor_data.sqlite', 'data/bow/bow_hahog_root_uchar_10000.npz', 'data/bow/bow_hahog_root_uchar_64.npz'):
        if (package / rel).exists():
            raise RuntimeError(f'Scoped asset must be absent: {rel}')
    from opensfm.dataset import DataSet
    from opensfm.sensors import sensor_data
    sensors = sensor_data()
    if len(sensors) != 3708 or sensors.get('acer ce-5330') != 5.75:
        raise RuntimeError('Unexpected JSON sensor fallback')
    with tempfile.TemporaryDirectory(prefix='scoped-opensfm-fixture-') as directory:
        root = Path(directory)
        (root / 'images').mkdir()
        (root / 'images/a.jpg').touch()
        if DataSet(str(root)).config['matcher_type'] != 'FLANN':
            raise RuntimeError('Unexpected scoped matching default')
        for setting in ('matcher_type: WORDS', 'matching_bow_neighbors: 1', 'matching_vlad_neighbors: 1'):
            (root / 'config.yaml').write_text(setting, encoding='utf-8')
            try:
                DataSet(str(root))
            except ValueError as error:
                if 'not supported' not in str(error):
                    raise
            else:
                raise RuntimeError(f'Unsupported mode was accepted: {setting}')
    print('PASS: scoped OpenSfM default, fallback and explicit unsupported-mode checks')


if __name__ == '__main__':
    main()
