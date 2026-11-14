#!/usr/bin/env python3
"""Test dense reconstruction with an externally supplied, hash-pinned scene.

The upstream test data's redistribution rights are unreviewed: never bundle it.
This is a bounded functional test, not accuracy or release validation.
"""
import argparse
import math
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

from openmvs_pointcloud_fixture import DATASET_FILES, verify_dataset


def validate_dense_ply(path: Path) -> int:
    data = path.read_bytes()
    if len(data) > 128*1024*1024 or b'end_header\n' not in data:
        raise ValueError('Invalid or oversized dense PLY')
    head, body = data.split(b'end_header\n', 1)
    lines = head.decode('ascii').splitlines()
    if lines[:2] != ['ply', 'format binary_little_endian 1.0']:
        raise ValueError('Unexpected dense PLY format')
    matches = [re.fullmatch(r'element vertex (\d+)', line) for line in lines]
    matches = [m for m in matches if m]
    if len(matches) != 1:
        raise ValueError('Missing dense point count')
    count = int(matches[0][1])
    if not 100 <= count <= 2_000_000:
        raise ValueError(f'Unexpected dense point count: {count}')
    expected = ['property float32 x', 'property float32 y', 'property float32 z',
                'property uint8 red', 'property uint8 green', 'property uint8 blue',
                'property float32 nx', 'property float32 ny', 'property float32 nz', 'property uint8 views']
    properties = [line for line in lines if line.startswith('property ')]
    if properties != expected or len(body) != count * 28:
        raise ValueError('Unexpected dense properties or truncated point data')
    for offset in range(0, len(body), 28):
        row = struct.unpack_from('<3f3B3fB', body, offset)
        if not all(math.isfinite(x) for x in (*row[:3], *row[6:9])) or row[9] == 0:
            raise ValueError('Nonfinite coordinates/normals or missing views')
    return count


def test_dense(executable: Path, source: Path, directory: Path) -> int:
    verify_dataset(source)
    for name in DATASET_FILES:
        target = directory/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/name, target)
    output = directory/'dense.mvs'
    command = [str(executable), '-i', str(directory/'scene.mvs'), '-o', str(output),
               '--archive-type', '1', '--resolution-level', '2', '--min-resolution', '320',
               '--max-threads', '2', '--cuda-device', '-2', '--geometric-iters', '0']
    completed = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=600)
    if completed.returncode != 0:
        raise ValueError(f'Dense reconstruction failed ({completed.returncode}): {completed.stdout[-5000:]} {completed.stderr[-1000:]}')
    if not output.is_file() or not (directory/'dense.ply').is_file():
        raise ValueError(f'Missing dense outputs: {completed.stdout[-3000:]}')
    return validate_dense_ply(directory/'dense.ply')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    parser.add_argument('--dataset', required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='dense-fixture-') as temp:
        count = test_dense(args.executable.resolve(), args.dataset.resolve(), Path(temp))
    print(f'PASS: CPU dense reconstruction produced {count} points; no accuracy or rights claim')


if __name__ == '__main__':
    main()
