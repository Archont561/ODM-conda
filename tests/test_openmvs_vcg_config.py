"""The vendored VCG must survive Conda's CMake include-root policy."""
import shutil
import subprocess

import pytest


def test_vcg_cache_path_bypasses_conda_rooted_find_path(tmp_path):
    cmake = shutil.which('cmake')
    if not cmake:
        pytest.skip('CMake is needed for this configure test')
    vcg = tmp_path / 'source' / '_external' / 'vcg'
    header = vcg / 'vcg/complex/complex.h'
    header.parent.mkdir(parents=True)
    header.write_text('// fixture\n', encoding='utf-8')
    project = tmp_path / 'project'
    project.mkdir()
    # Same find_path expression as the pinned OpenMVS FindVCG.cmake module.
    (project / 'CMakeLists.txt').write_text(
        'cmake_minimum_required(VERSION 3.16)\nproject(vcg_test NONE)\n'
        'find_path(VCG_DIR "vcg/complex/complex.h" HINTS "${VCG_ROOT}" '
        'PATH_SUFFIXES "vcg" "include")\n'
        'if(NOT EXISTS "${VCG_DIR}/vcg/complex/complex.h")\n'
        '  message(FATAL_ERROR "VCG not found")\nendif()\n', encoding='utf-8')
    common = [cmake, '-S', str(project), f'-DCMAKE_FIND_ROOT_PATH={tmp_path / "host"}',
              '-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY']
    without_cache = subprocess.run([*common, '-B', str(tmp_path / 'bad'), f'-DVCG_ROOT={vcg}'],
                                   text=True, capture_output=True, timeout=30)
    assert without_cache.returncode != 0
    with_cache = subprocess.run([*common, '-B', str(tmp_path / 'good'), f'-DVCG_DIR:PATH={vcg}'],
                                text=True, capture_output=True, timeout=30)
    assert with_cache.returncode == 0, with_cache.stdout + with_cache.stderr
    assert f'VCG_DIR:PATH={vcg}' in (tmp_path / 'good/CMakeCache.txt').read_text().splitlines()
