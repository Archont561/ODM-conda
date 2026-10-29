#!/usr/bin/env python3
"""Generate a synthetic OpenMVS scene for research-only reconstruction testing.

The binary scene encodes version 3 of the upstream OpenMVS interface format.
This fixture has not been run against an installed or isolated Conda package.
"""
from __future__ import annotations

import argparse
import math
import struct
import subprocess
import tempfile
from pathlib import Path

from openmvs_pointcloud_fixture import check_missing_visibility, validate_mesh
from openmvs_fixture import test_openmvs as clean_cube
from texrecon_fixture import write_gradient_png


def generate_scene(directory: Path) -> Path:
    """Two calibrated cameras observe 400 points on a gently curved surface."""
    write_gradient_png(directory / 'view0.png')
    write_gradient_png(directory / 'view1.png')
    data = bytearray(b'MVSI' + struct.pack('<II', 3, 0))

    def u32(value: int) -> None:
        data.extend(struct.pack('<I', value))

    def u64(value: int) -> None:
        data.extend(struct.pack('<Q', value))

    def text(value: str) -> None:
        encoded = value.encode('utf-8')
        u64(len(encoded))
        data.extend(encoded)

    def floats(values: list[float]) -> None:
        data.extend(struct.pack(f'<{len(values)}f', *values))

    def doubles(values: list[float]) -> None:
        data.extend(struct.pack(f'<{len(values)}d', *values))

    identity = [1., 0., 0., 0., 1., 0., 0., 0., 1.]
    intrinsics = [60., 0., 32., 0., 60., 32., 0., 0., 1.]
    u64(1)  # platforms
    text('synthetic')
    u64(1)  # cameras
    text('camera')
    u32(64)
    u32(64)
    doubles(intrinsics)
    doubles(identity)
    doubles([0., 0., 0.])
    u64(2)  # platform poses
    for x in (-0.4, 0.4):
        doubles(identity)
        doubles([x, 0., 0.])
    u64(2)  # images
    for index in range(2):
        text(f'view{index}.png')
        u32(0)  # platform
        u32(0)  # camera
        u32(index)  # pose
        u32(index)  # image ID
    u64(400)  # vertices
    for y in range(20):
        for x in range(20):
            px, py = (x - 9.5) * 0.07, (y - 9.5) * 0.07
            floats([px, py, 4 + 0.18 * math.cos(px * 3) * math.cos(py * 3)])
            u64(2)
            for index in range(2):
                u32(index)
                floats([1.0])
    for _ in range(5):  # optional point normals, colors, lines, line normals and colors
        u64(0)
    doubles([1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.])
    path = directory / 'scene.mvs'
    path.write_bytes(data)
    return path


def test_reconstruction(executable: Path, directory: Path) -> tuple[int, int]:
    scene = generate_scene(directory)
    output = directory / 'result.mvs'
    command = [str(executable), '-i', str(scene), '-o', str(output), '--archive-type', '1',
               '--min-point-distance', '0', '--remove-spurious', '0', '--remove-spikes', '0',
               '--close-holes', '0', '--smooth', '0', '--max-threads', '1']
    result = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, f'ReconstructMesh failed: {result.stdout}\n{result.stderr}'
    mesh = directory / 'result.ply'
    assert mesh.is_file() and output.is_file(), 'Missing reconstruction output'
    assert 'Mesh reconstruction completed:' in result.stdout, 'Missing reconstruction evidence'
    vertices, faces = validate_mesh(mesh, min_vertices=20, min_faces=20)
    body = mesh.read_bytes().split(b'end_header\n', 1)[1]
    points = [struct.unpack_from('<3f', body, offset) for offset in range(0, vertices * 12, 12)]
    assert all(-1.0 <= x <= 1.0 and -1.0 <= y <= 1.0 and 3.7 <= z <= 4.3 for x, y, z in points), 'Unexpected reconstruction geometry'
    return vertices, faces



def generate_visible_cloud(path: Path, *, views: tuple[int, ...] = (0, 1)) -> Path:
    """Write a separate ASCII PLY using an explicit uchar-count uint-index list."""
    with path.open('w', encoding='ascii') as out:
        out.write('ply\nformat ascii 1.0\nelement vertex 400\n'
                  'property float x\nproperty float y\nproperty float z\n'
                  'property uchar views\nproperty list uchar uint view_indices\nend_header\n')
        for y in range(20):
            for x in range(20):
                px, py = (x - 9.5) * 0.07, (y - 9.5) * 0.07
                z = 4 + 0.18 * math.cos(px * 3) * math.cos(py * 3)
                indices = ' '.join(str(index) for index in views)
                out.write(f'{px} {py} {z} {len(views)} {len(views)} {indices}\n')
    return path


def test_separate_reconstruction(executable: Path, directory: Path) -> tuple[int, int]:
    scene = generate_scene(directory)
    cloud = generate_visible_cloud(directory / 'visible.ply')
    output = directory / 'separate-result.mvs'
    command = [str(executable), '-i', str(scene), '-p', str(cloud), '-o', str(output), '--archive-type', '1',
               '--min-point-distance', '0', '--remove-spurious', '0', '--remove-spikes', '0',
               '--close-holes', '0', '--smooth', '0', '--max-threads', '1']
    result = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, f'Separate point-cloud reconstruction failed: {result.stdout}\n{result.stderr}'
    mesh = directory / 'separate-result.ply'
    assert mesh.is_file() and output.is_file(), 'Missing reconstruction output'
    assert 'Mesh reconstruction completed:' in result.stdout, 'Missing reconstruction evidence'
    vertices, faces = validate_mesh(mesh, min_vertices=20, min_faces=20)
    body = mesh.read_bytes().split(b'end_header\n', 1)[1]
    points = [struct.unpack_from('<3f', body, offset) for offset in range(0, vertices * 12, 12)]
    assert all(-1.0 <= x <= 1.0 and -1.0 <= y <= 1.0 and 3.7 <= z <= 4.3 for x, y, z in points), 'Unexpected reconstruction geometry'
    return vertices, faces


def check_invalid_view_list(executable: Path, directory: Path, views: tuple[int, ...]) -> None:
    scene = generate_scene(directory)
    cloud = generate_visible_cloud(directory / 'invalid-views.ply', views=views)
    result = subprocess.run([str(executable), '-i', str(scene), '-p', str(cloud), '-o', str(directory / 'invalid-result.mvs'),
                             '--archive-type', '1', '--min-point-distance', '0', '--max-threads', '1'],
                            cwd=directory, text=True, capture_output=True, timeout=120)
    assert result.returncode > 0, f'Expected clean rejection, got exit {result.returncode}'
    assert 'point cloud requires per-point camera visibility' in (result.stdout + result.stderr).lower(), 'Missing visibility error'
    assert not (directory / 'invalid-result.ply').exists(), 'Unexpected reconstruction output'


def check_invalid_schema(executable: Path, directory: Path, property_line: str) -> None:
    scene = generate_scene(directory)
    cloud = generate_visible_cloud(directory / 'bad-schema.ply')
    data = cloud.read_text(encoding='ascii').replace('property list uchar uint view_indices', property_line)
    cloud.write_text(data, encoding='ascii')
    output = directory / 'bad-schema-result.mvs'
    result = subprocess.run([str(executable), '-i', str(scene), '-p', str(cloud), '-o', str(output),
                             '--max-threads', '1'], cwd=directory, text=True, capture_output=True, timeout=120)
    assert result.returncode > 0, f'Expected clean schema rejection, got exit {result.returncode}'
    assert 'cannot load point-cloud file' in (result.stdout + result.stderr).lower(), 'Missing load diagnostic'
    assert not output.exists() and not output.with_suffix('.ply').exists(), 'Unexpected output'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='openmvs-synthetic-') as directory:
        vertices, faces = test_reconstruction(args.executable.resolve(), Path(directory))
    print(f'PASS: synthetic OpenMVS scene reconstructed to {vertices} vertices and {faces} faces')
    for counts in (False, True):
        with tempfile.TemporaryDirectory(prefix='openmvs-synthetic-invalid-') as directory:
            work = Path(directory)
            scene = generate_scene(work)
            check_missing_visibility(args.executable.resolve(), scene, work, with_view_counts=counts)
    print('PASS: separate PLYs without camera indices are rejected without crashing')
    with tempfile.TemporaryDirectory(prefix='openmvs-synthetic-separate-') as directory:
        vertices, faces = test_separate_reconstruction(args.executable.resolve(), Path(directory))
    print(f'PASS: separate PLY with camera indices reconstructed to {vertices} vertices and {faces} faces')
    for views in ((), (0, 2), (0, 0), (1, 0)):
        with tempfile.TemporaryDirectory(prefix='openmvs-invalid-views-') as directory:
            check_invalid_view_list(args.executable.resolve(), Path(directory), views)
    print('PASS: empty, out-of-range, duplicate and unsorted camera index lists are rejected without crashing')
    for schema in ('property uint view_indices', 'property list uchar int view_indices',
                   'property list uint uint view_indices'):
        with tempfile.TemporaryDirectory(prefix='openmvs-invalid-schema-') as directory:
            check_invalid_schema(args.executable.resolve(), Path(directory), schema)
    print('PASS: invalid view index schemas are rejected without crashing')
    with tempfile.TemporaryDirectory(prefix='openmvs-synthetic-clean-') as directory:
        clean_cube(args.executable.resolve(), Path(directory))
    print('PASS: generated cube mesh cleaned and decimated')


if __name__ == '__main__':
    main()
