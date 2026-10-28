"""The research CMake harness must actually disable pybind's test tree."""
import shutil
import subprocess

import pytest

from common import ROOT


def test_pybind_research_harness_disables_subproject_tests(tmp_path):
    cmake, compiler = shutil.which('cmake'), shutil.which('c++')
    if not cmake or not compiler:
        pytest.skip('CMake and a C++ compiler are needed for this configure test')
    source = tmp_path / 'pybind'
    source.mkdir()
    (source / 'CMakeLists.txt').write_text(
        'if(PYBIND11_TEST OR BUILD_TESTING OR NOT FETCHCONTENT_FULLY_DISCONNECTED)\n'
        '  message(FATAL_ERROR "unsafe test configuration")\n'
        'endif()\n', encoding='utf-8')
    result = subprocess.run([cmake, '-S', str(ROOT / 'research/pybind11-tests-disabled'),
                             '-B', str(tmp_path / 'build'), f'-DPYBIND11_SOURCE={source}',
                             '-DPYBIND11_TEST=ON', '-DBUILD_TESTING=ON',
                             '-DFETCHCONTENT_FULLY_DISCONNECTED=OFF'],
                            text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    cache = (tmp_path / 'build' / 'CMakeCache.txt').read_text(encoding='utf-8')
    assert 'PYBIND11_TEST:BOOL=OFF' in cache
    assert 'BUILD_TESTING:BOOL=OFF' in cache
    assert 'FETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON' in cache
