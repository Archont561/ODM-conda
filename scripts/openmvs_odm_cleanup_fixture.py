#!/usr/bin/env python3
"""Private TetraFlow test of ODM's two ReconstructMesh cleanup command shapes."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from openmvs_fixture import CUBE, validate_mesh


def check(executable: Path, directory: Path, spurious: str) -> None:
    source = directory / 'input.ply'
    output = directory / 'mesh.ply'
    source.write_text(CUBE, encoding='ascii')
    # opendm/mesh.py: both dem_to_mesh_gridded and screened_poisson_reconstruction
    # use this shape; only the spurious-removal value differs.
    command = [str(executable), '-i', str(source), '-o', str(output), '--archive-type', '3',
               '--remove-spikes', '0', '--remove-spurious', spurious, '--smooth', '0',
               '--target-face-num', '8', '-v', '0']
    result = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, f'ODM cleanup failed: {result.stdout}\n{result.stderr}'
    assert output.is_file(), 'ODM-expected output path is missing'
    validate_mesh(output)


def main() -> None:
    executable = Path(sys.argv[1]).resolve()
    for spurious in ('0', '20'):
        with tempfile.TemporaryDirectory(prefix='openmvs-odm-cleanup-') as tmp:
            check(executable, Path(tmp), spurious)
    print('PASS: ODM gridded and Poisson mesh cleanup command shapes')


if __name__ == '__main__':
    main()
