#!/usr/bin/env python3
"""Generated weighted PLY checks for the private TetraFlow experiment only."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from openmvs_synthetic_fixture import generate_scene, generate_visible_cloud
from openmvs_pointcloud_fixture import validate_mesh


def check(executable: Path, directory: Path, *, property_line: str, weights: str, valid: bool) -> None:
    scene = generate_scene(directory)
    cloud = generate_visible_cloud(directory / 'cloud.ply', scalar_views=False)
    header, body = cloud.read_text().split('end_header\n', 1)
    lines = body.splitlines()
    cloud.write_text(header + f'{property_line}\nend_header\n' + ''.join(line + ' ' + weights + '\n' for line in lines))
    output = directory / 'out.mvs'
    command = [str(executable), '-i', str(scene), '-p', str(cloud), '-o', str(output),
               '--archive-type', '1', '--min-point-distance', '0', '--remove-spurious', '0',
               '--remove-spikes', '0', '--close-holes', '0', '--smooth', '0', '--max-threads', '1']
    result = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    if valid:
        assert result.returncode == 0, result.stdout + result.stderr
        assert output.is_file() and output.with_suffix('.ply').is_file()
        validate_mesh(output.with_suffix('.ply'), min_vertices=20, min_faces=20)
    else:
        assert result.returncode > 0, f'Expected clean rejection, got {result.returncode}'
        assert 'cannot load point-cloud file' in (result.stdout + result.stderr).lower()
        assert not output.exists() and not output.with_suffix('.ply').exists()


def main() -> None:
    executable = Path(sys.argv[1]).resolve()
    for property_line, weights, valid in (
        ('property list uchar float view_weights', '2 0.8 0.9', True),
        ('property list uchar float view_weights', '1 0.8', False),
        ('property float view_weights', '0.8', False),
        ('property list uint float view_weights', '2 0.8 0.9', False),
    ):
        with tempfile.TemporaryDirectory(prefix='openmvs-weighted-') as directory:
            check(executable, Path(directory), property_line=property_line, weights=weights, valid=valid)
    print('PASS: weighted PLY valid and malformed cases')


if __name__ == '__main__':
    main()
