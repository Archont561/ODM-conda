"""OpenMVS research builds must reject restricted named linker inputs."""
import shutil
import subprocess

import pytest

from common import ScaffoldError
from openmvs_link_map import verify_openmvs_link_map


GOOD = '''Archive member included to satisfy reference by file (symbol)
/work/libMVS.a(SceneReconstruct.cpp.o) app (reconstruct)
Memory Configuration
Linker script and memory map
LOAD /work/libMVS.a
LOAD /work/libMath.a
LOAD /work/ReconstructMesh.cpp.o
OUTPUT(bin/ReconstructMesh elf64-x86-64)
'''


def test_valid_map_and_incomplete_map(tmp_path):
    path = tmp_path / 'link.map'
    path.write_text(GOOD)
    assert len(verify_openmvs_link_map(path)) == 64
    path.write_text('LOAD libMVS.a\n')
    with pytest.raises(ScaffoldError, match='incomplete'):
        verify_openmvs_link_map(path)


@pytest.mark.parametrize('bad', ['libs/Math/IBFS/IBFS.cpp.o', 'libs/Math/TRWS/instances.cpp.o',
                                  'libMath.a(IBFS.cpp.o)', 'MRFEnergy<double>::Minimize()',
                                  'libs/MVS/SceneDensify.cpp.o'])
def test_restricted_named_input_rejected(tmp_path, bad):
    path = tmp_path / 'link.map'
    path.write_text(GOOD + bad + '\n')
    with pytest.raises(ScaffoldError, match='restricted'):
        verify_openmvs_link_map(path)


def test_missing_symlink_and_invalid_text(tmp_path):
    path = tmp_path / 'link.map'
    with pytest.raises(ScaffoldError):
        verify_openmvs_link_map(path)
    path.symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError):
        verify_openmvs_link_map(path)
    path.unlink()
    path.write_bytes(b'\xff')
    with pytest.raises(ScaffoldError):
        verify_openmvs_link_map(path)


def test_real_gnu_link_map(tmp_path):
    cxx, ar = shutil.which('g++'), shutil.which('ar')
    if not cxx or not ar:
        pytest.skip('GNU C++ and ar required')
    sources = {'SceneReconstruct.cpp': 'int reconstruct() { return 1; }',
               'math.cpp': 'int math() { return 2; }',
               'ReconstructMesh.cpp': 'int reconstruct(); int math(); int main() { return reconstruct() + math(); }'}
    for name, code in sources.items():
        (tmp_path / name).write_text(code)
        subprocess.run([cxx, '-c', str(tmp_path / name), '-o', str(tmp_path / (name + '.o'))], check=True)
    for archive, obj in [('libMVS.a', 'SceneReconstruct.cpp.o'), ('libMath.a', 'math.cpp.o')]:
        subprocess.run([ar, 'rcs', str(tmp_path / archive), str(tmp_path / obj)], check=True)
    path = tmp_path / 'link.map'
    subprocess.run([cxx, str(tmp_path / 'ReconstructMesh.cpp.o'), str(tmp_path / 'libMVS.a'),
                    str(tmp_path / 'libMath.a'), f'-Wl,-Map={path}', '-o', str(tmp_path / 'ReconstructMesh')], check=True)
    assert len(verify_openmvs_link_map(path)) == 64
