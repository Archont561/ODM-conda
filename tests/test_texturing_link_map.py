import pytest

from common import ScaffoldError
from texturing_link_map import verify_texturing_link_map


GOOD_MAP = '''Archive member included to satisfy reference by file (symbol)
/work/.native-mve/libs/mve/libmve.a(mesh.cc.o)
                              texrecon.cpp.o (mesh)
Memory Configuration
Linker script and memory map
LOAD /work/.native-mve/libs/mve/libmve.a
LOAD /work/.native-mve/libs/util/libmve_util.a
LOAD /work/apps/texrecon/CMakeFiles/texrecon.dir/texrecon.cpp.o
OUTPUT(texrecon elf64-x86-64)
'''


def test_texturing_link_map_requires_real_link_evidence(tmp_path):
    path = tmp_path / 'texrecon.map'
    path.write_text(GOOD_MAP, encoding='utf-8')
    verify_texturing_link_map(path)
    path.write_text('LOAD libmve.a\nLOAD libmve_util.a\n', encoding='utf-8')
    with pytest.raises(ScaffoldError, match='incomplete'):
        verify_texturing_link_map(path)


@pytest.mark.parametrize('forbidden', [
    'LOAD /work/libs/sfm/libmve_sfm.a',
    '/work/libs/sfm/sift.cc.o',
    '/work/libs/sfm/surf.cc.o',
])
def test_texturing_link_map_rejects_sfm_or_restricted_objects(tmp_path, forbidden):
    path = tmp_path / 'texrecon.map'
    path.write_text(GOOD_MAP + forbidden + '\n', encoding='utf-8')
    with pytest.raises(ScaffoldError, match='SIFT/SURF'):
        verify_texturing_link_map(path)


def test_texturing_link_map_rejects_missing_or_symlink(tmp_path):
    path = tmp_path / 'texrecon.map'
    with pytest.raises(ScaffoldError, match='link map'):
        verify_texturing_link_map(path)
    path.symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='link map'):
        verify_texturing_link_map(path)


def test_texturing_link_map_with_real_gnu_linker(tmp_path):
    import shutil
    import subprocess

    cxx, ar = shutil.which('g++'), shutil.which('ar')
    if not cxx or not ar:
        pytest.skip('GNU C++ compiler and ar are not available')
    source = {'mesh.cc': 'int mesh() { return 1; }',
              'util.cc': 'int util() { return 2; }',
              'texrecon.cpp': 'int mesh(); int util(); int main() { return mesh() + util(); }'}
    for name, content in source.items():
        (tmp_path / name).write_text(content, encoding='utf-8')
        subprocess.run([cxx, '-c', str(tmp_path / name), '-o', str(tmp_path / (name + '.o'))], check=True)
    for archive, obj in [('libmve.a', 'mesh.cc.o'), ('libmve_util.a', 'util.cc.o')]:
        subprocess.run([ar, 'rcs', str(tmp_path / archive), str(tmp_path / obj)], check=True)
    link_map = tmp_path / 'actual.map'
    subprocess.run([cxx, str(tmp_path / 'texrecon.cpp.o'), str(tmp_path / 'libmve.a'),
                    str(tmp_path / 'libmve_util.a'), f'-Wl,-Map={link_map}', '-o', str(tmp_path / 'texrecon')], check=True)
    assert len(verify_texturing_link_map(link_map)) == 64
