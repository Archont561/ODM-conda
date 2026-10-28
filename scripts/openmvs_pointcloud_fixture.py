#!/usr/bin/env python3
"""Research fixture using the pinned OpenMVS upstream test scene, not package validation.

Dataset licensing and suitability for redistribution remain unreviewed. The
caller supplies the files from the pinned source tree; none are bundled here.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

DATASET_FILES = {
    'scene.mvs': 'dc060a7e72eb05e87500c1ea31b5efda89d278d53acaf7429b90bb0691ba46fb',
    'images/00000.jpg': '6cccce6a76a69b9deb749975e8230633ecb946cc704f9d5a69da49615307b32c',
    'images/00001.jpg': '3972675ea769df79116a5aedc8548faf5c9611a3198e3cd09cba888b2e19b097',
    'images/00002.jpg': '10d3a8c35da692260f3b5d4a6f3b1f0a8c1b790b06200c56db14eba2bc3d72c4',
    'images/00003.jpg': '55d082d26b497fd491140da8ca95f56eb3050edfd481ea094d9f1f8a5ad83980',
}


def verify_dataset(source: Path) -> None:
    for name, expected in DATASET_FILES.items():
        path = source / name
        assert path.is_file(), f'Missing dataset file: {name}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'Dataset hash mismatch: {name}'


def validate_mesh(path: Path, min_vertices: int = 100, min_faces: int = 100) -> tuple[int, int]:
    data = path.read_bytes()
    marker = b'end_header\n'
    assert marker in data, 'Invalid mesh header'
    header, body = data.split(marker, 1)
    lines = header.decode('ascii').splitlines()
    assert len(lines) == 8 and lines[:2] == ['ply', 'format binary_little_endian 1.0'], 'Unexpected mesh format'
    assert lines[2].startswith('element vertex ') and lines[6].startswith('element face '), 'Invalid mesh elements'
    assert lines[3:6] == ['property float32 x', 'property float32 y', 'property float32 z'], 'Invalid vertex properties'
    assert lines[7] == 'property list uint8 uint32 vertex_indices', 'Invalid face properties'
    vertices, faces = int(lines[2].split()[-1]), int(lines[6].split()[-1])
    assert min_vertices <= vertices <= 1_000_000 and min_faces <= faces <= 2_000_000, 'Unexpected mesh size'
    assert len(body) == vertices * 12 + faces * 13, 'Invalid mesh length'
    for offset in range(0, vertices * 12, 12):
        assert all(math.isfinite(value) for value in struct.unpack_from('<3f', body, offset)), 'Invalid vertex'
    for offset in range(vertices * 12, len(body), 13):
        count, a, b, c = struct.unpack_from('<B3I', body, offset)
        assert count == 3 and len({a, b, c}) == 3 and max(a, b, c) < vertices, 'Invalid triangle'
    return vertices, faces


def test_pointcloud(executable: Path, source: Path, directory: Path) -> tuple[int, int]:
    verify_dataset(source)
    for name in DATASET_FILES:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    result = directory / 'result.mvs'
    command = [str(executable), '-i', str(directory / 'scene.mvs'), '-o', str(result),
               '--archive-type', '1', '--min-point-distance', '0', '--remove-spurious', '0',
               '--remove-spikes', '0', '--close-holes', '0', '--smooth', '0', '--max-threads', '1']
    completed = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    assert completed.returncode == 0, f'ReconstructMesh failed: {completed.stdout}\n{completed.stderr}'
    mesh = directory / 'result.ply'
    assert mesh.is_file() and result.is_file(), 'Missing reconstruction output'
    assert 'Mesh reconstruction completed:' in completed.stdout, 'Missing reconstruction evidence'
    return validate_mesh(mesh)


def test_missing_visibility(executable: Path, source: Path, directory: Path, *, with_view_counts: bool = False) -> None:
    """A point cloud without view indices must be rejected instead of crashing."""
    verify_dataset(source)
    for name in DATASET_FILES:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    check_missing_visibility(executable, directory / 'scene.mvs', directory, with_view_counts=with_view_counts)


def check_missing_visibility(executable: Path, scene: Path, directory: Path, *, with_view_counts: bool = False) -> None:
    """Check that separate PLY without camera indices fails without a signal."""
    cloud = directory / 'no-views.ply'
    with cloud.open('w', encoding='ascii') as output:
        output.write('ply\nformat ascii 1.0\nelement vertex 400\n'
                     'property float x\nproperty float y\nproperty float z\n')
        if with_view_counts:
            output.write('property uchar views\n')
        output.write('end_header\n')
        for i in range(20):
            for j in range(20):
                output.write(f'{i * 0.05} {j * 0.05} {1 + ((i + j) % 3) * 0.02}'
                             + (' 2' if with_view_counts else '') + '\n')
    command = [str(executable), '-i', str(scene), '-p', str(cloud),
               '-o', str(directory / 'result.mvs'), '--archive-type', '1',
               '--min-point-distance', '0', '--max-threads', '1']
    completed = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    assert completed.returncode > 0, f'Expected a clean error, got exit {completed.returncode}'
    assert 'point cloud requires per-point camera visibility' in (completed.stdout + completed.stderr).lower(), 'Missing visibility error'
    assert not (directory / 'result.ply').exists(), 'Unexpected output for invalid point cloud'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    parser.add_argument('--dataset', required=True, type=Path, help='Pinned upstream apps/Tests/data directory')
    parser.add_argument('--check-visibility-rejection', action='store_true',
                        help='Also check rejection of PLY without camera IDs (requires experimental patch)')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='openmvs-pointcloud-') as directory:
        vertices, faces = test_pointcloud(args.executable.resolve(), args.dataset.resolve(), Path(directory))
    print(f'PASS: research OpenMVS point-cloud reconstruction produced {vertices} vertices and {faces} faces')
    if args.check_visibility_rejection:
        for counts in (False, True):
            with tempfile.TemporaryDirectory(prefix='openmvs-no-visibility-') as directory:
                test_missing_visibility(args.executable.resolve(), args.dataset.resolve(), Path(directory), with_view_counts=counts)
        print('PASS: point clouds without camera IDs are rejected without crashing')


if __name__ == '__main__':
    main()
