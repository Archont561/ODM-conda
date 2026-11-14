#!/usr/bin/env python3
"""Build CPU OpenPointClass with staged LightGBM; never a release approval."""
import os
import platform
import shlex
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, run, sha256

CMAKE_SHA256 = '36847f62301e1a39692b213834dda3f8124739168994890f467cb37a7518f573'


def prepare_cmake(source: Path, archive: Path) -> None:
    cmake = source/'CMakeLists.txt'
    if cmake.is_symlink() or not cmake.is_file() or sha256(cmake) != CMAKE_SHA256:
        raise ScaffoldError('Unexpected OpenPointClass build source')
    if archive.is_symlink() or not archive.is_file():
        raise ScaffoldError('Missing staged LightGBM static archive')
    text = cmake.read_text()
    start = text.index('if((CMAKE_CXX_COMPILER_ID MATCHES')
    end = text.index('find_package(OpenMP REQUIRED)', start)
    text = text[:start] + '# Research build uses conda compiler baseline, never -march=native.\n\n' + text[end:]
    start = text.index('if (WITH_GBT)\n    message("Building with GBT support")')
    end = text.index('include_directories(${EIGEN3_INCLUDE_DIR})', start)
    replacement = '''if (WITH_GBT)
    add_library(lib_lightgbm STATIC IMPORTED)
    set_target_properties(lib_lightgbm PROPERTIES IMPORTED_LOCATION "@ARCHIVE@")
    set(LIGHTGBM_LIB_PATH "@ARCHIVE@")
    include_directories("${CMAKE_CURRENT_SOURCE_DIR}/_external/lightgbm/include")
endif()

'''.replace('@ARCHIVE@', str(archive))
    text = text[:start] + replacement + text[end:]
    # Removed ExternalProject dependency; static archive is built before CMake.
    old = '    add_dependencies(libopc lightgbm)\n'
    if text.count(old) != 1:
        raise ScaffoldError('Unexpected LightGBM dependency stanza')
    cmake.write_text(text.replace(old, ''))


def main():
    if os.environ.get('PKG_NAME') != 'openpointclass-research' or platform.system() != 'Linux' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise ScaffoldError('Research package requires linux-64')
    if any(not os.environ.get(k) for k in ('PREFIX', 'BUILD_PREFIX', 'SRC_DIR')):
        raise ScaffoldError('Missing isolated build inputs')
    prefix = Path(os.environ['PREFIX']).resolve()
    source = Path(os.environ['SRC_DIR']).resolve()
    if prefix in (source, ROOT, Path('/')) or source in (ROOT, Path('/')):
        raise ScaffoldError('Unsafe build paths')
    lightgbm = source/'_external/lightgbm'
    if not all((lightgbm/p).is_file() for p in ('CMakeLists.txt', 'include/LightGBM/boosting.h', 'external_libs/fmt/include/fmt/format.h', 'external_libs/fast_double_parser/include/fast_double_parser.h')):
        raise ScaffoldError('Missing staged LightGBM sources')
    env = os.environ.copy(); env['CONDA_PREFIX'] = str(prefix); env['CMAKE_PREFIX_PATH'] = str(prefix)
    flags = f"{env.get('CXXFLAGS', '')} -march=x86-64 -mno-popcnt -I{prefix/'include/eigen3'}"
    build = source/'.lightgbm-build'
    common = ['-G', 'Ninja', *shlex.split(env.get('CMAKE_ARGS', '')), '-DCMAKE_BUILD_TYPE=Release',
              f'-DCMAKE_PREFIX_PATH={prefix}', f'-DCMAKE_CXX_FLAGS={flags}', '-DFETCHCONTENT_FULLY_DISCONNECTED=ON']
    run(['cmake', '-S', str(lightgbm), '-B', str(build), *common,
         '-DBUILD_STATIC_LIB=ON', '-DUSE_GPU=OFF', '-DUSE_CUDA=OFF', '-DUSE_OPENMP=ON'], cwd=source, env=env)
    run(['cmake', '--build', str(build), '--target', '_lightgbm', '--parallel', '2'], cwd=source, env=env)
    archives = list(build.rglob('lib_lightgbm.a')) + list(lightgbm.glob('lib_lightgbm.a'))
    if len(archives) != 1:
        raise ScaffoldError('Expected exactly one staged LightGBM archive')
    prepare_cmake(source, archives[0])
    opcbuild = source/'.opc-build'
    run(['cmake', '-S', str(source), '-B', str(opcbuild), *common,
         '-DWITH_PDAL=ON', '-DWITH_GBT=ON', '-DBUILD_PCTRAIN=OFF', '-DBUILD_PCCLASSIFY=ON'], cwd=source, env=env)
    run(['cmake', '--build', str(opcbuild), '--target', 'pcclassify', '--parallel', '2'], cwd=source, env=env)
    binary = opcbuild/'pcclassify'
    if not binary.is_file(): raise ScaffoldError('Missing classifier')
    (prefix/'bin').mkdir(parents=True, exist_ok=True); shutil.copy2(binary, prefix/'bin/pcclassify')
    share = prefix/'share/odm-conda/openpointclass-research'; share.mkdir(parents=True, exist_ok=True)
    (share/'SOURCE.txt').write_text('PRIVATE RESEARCH ONLY: model and source rights unreviewed.\n')


if __name__ == '__main__':
    fail_cli(main)
