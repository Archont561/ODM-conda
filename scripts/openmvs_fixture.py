#!/usr/bin/env python3
"""Research-only OpenMVS mesh-cleaning fixture; not a reconstruction test."""
from __future__ import annotations

import argparse
import math
import struct
import subprocess
import tempfile
from pathlib import Path


CUBE = """ply
format ascii 1.0
element vertex 8
property float x
property float y
property float z
element face 12
property list uchar int vertex_indices
end_header
0 0 0
1 0 0
1 1 0
0 1 0
0 0 1
1 0 1
1 1 1
0 1 1
3 0 2 1
3 0 3 2
3 4 5 6
3 4 6 7
3 0 1 5
3 0 5 4
3 1 2 6
3 1 6 5
3 2 3 7
3 2 7 6
3 3 0 4
3 3 4 7
"""


def validate_mesh(path: Path) -> None:
    data = path.read_bytes()
    marker = b'end_header\n'
    assert marker in data, 'Invalid mesh header'
    header, body = data.split(marker, 1)
    lines = header.decode('ascii').splitlines()
    assert lines[:2] == ['ply', 'format binary_little_endian 1.0'], 'Unexpected mesh format'
    assert lines[3:6] == ['property float32 x', 'property float32 y', 'property float32 z']
    assert lines[7:] == ['property list uint8 uint32 vertex_indices']
    assert lines[2].startswith('element vertex ') and lines[6].startswith('element face ')
    vertices, faces = int(lines[2].split()[-1]), int(lines[6].split()[-1])
    assert 4 <= vertices < 8 and 4 <= faces < 12, 'Cube was not decimated'
    assert len(body) == vertices * 12 + faces * 13, 'Invalid mesh length'
    for offset in range(0, vertices * 12, 12):
        vertex = struct.unpack_from('<3f', body, offset)
        assert all(math.isfinite(value) and -0.001 <= value <= 1.001 for value in vertex), 'Invalid cube vertex'
    for offset in range(vertices * 12, len(body), 13):
        count, a, b, c = struct.unpack_from('<B3I', body, offset)
        assert count == 3 and len({a, b, c}) == 3 and max(a, b, c) < vertices, 'Invalid triangle'


def test_openmvs(executable: Path, directory: Path) -> None:
    """Clean and decimate a cube; this deliberately skips scene reconstruction."""
    source, output = directory / 'cube.ply', directory / 'out.mvs'
    source.write_text(CUBE, encoding='ascii')
    command = [str(executable), '-i', str(source), '-o', str(output), '--decimate', '0.9',
               '--remove-spurious', '0', '--remove-spikes', '0', '--close-holes', '0',
               '--smooth', '0', '--max-threads', '1']
    completed = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, f'ReconstructMesh failed: {completed.stdout}\n{completed.stderr}'
    mesh = directory / 'out.ply'
    assert mesh.is_file(), 'Missing output mesh'
    validate_mesh(mesh)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='openmvs-fixture-') as directory:
        test_openmvs(args.executable.resolve(), Path(directory))
    print('PASS: research OpenMVS cleaned and decimated a generated cube mesh')


if __name__ == '__main__':
    main()
