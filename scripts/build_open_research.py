#!/usr/bin/env python3
"""Build the two local-only research recipes inside rattler-build.

This does not establish license completeness or permission to distribute either
package or its upstream archives. No production component is registered here.
"""
from __future__ import annotations

import os
import platform
import shlex
import shutil
import subprocess
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, run
from openmvs_graph_policy import verify_openmvs_tree
from opensfm_graph_policy import verify_opensfm_tree


def main() -> None:
    name = os.environ.get('PKG_NAME', '')
    if name not in ('openmvs-odm', 'opensfm-odm'):
        raise ScaffoldError('Unsupported research component')
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise ScaffoldError('Research builds are linux-64 only')
    for variable in ('PREFIX', 'BUILD_PREFIX', 'SRC_DIR'):
        if not os.environ.get(variable):
            raise ScaffoldError(f'Missing rattler-build environment variable: {variable}')
    prefix, build_prefix, source = (Path(os.environ[key]).resolve() for key in ('PREFIX', 'BUILD_PREFIX', 'SRC_DIR'))
    if prefix in (build_prefix, source, ROOT, Path('/')) or source in (ROOT, Path('/')):
        raise ScaffoldError('Refusing an unsafe build or installation prefix')
    if name == 'openmvs-odm':
        verify_openmvs_tree(source)
    else:
        verify_opensfm_tree(source)

    env = os.environ.copy()
    env['CONDA_PREFIX'] = str(prefix)
    env['CMAKE_PREFIX_PATH'] = str(prefix)
    build = source / '.research-build'
    args = ['cmake', '-S', str(source if name == 'openmvs-odm' else source / 'opensfm/src'),
            '-B', str(build), '-G', 'Ninja', *shlex.split(env.get('CMAKE_ARGS', '')),
            '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_PREFIX_PATH={prefix}',
            f'-DCMAKE_INSTALL_PREFIX={prefix}', '-DBUILD_TESTING=OFF',
            '-DFETCHCONTENT_FULLY_DISCONNECTED=ON',
            f"-DCMAKE_CXX_FLAGS={env.get('CXXFLAGS', '')} -march=x86-64 -mno-popcnt -DEIGEN_MPL2_ONLY"]
    if name == 'openmvs-odm':
        args += [f"-DVCG_ROOT={source / '_external/vcg'}", f"-DEIGEN3_INCLUDE_DIR={source / '_external/eigen'}",
                 '-DOpenMVS_USE_CUDA=OFF', '-DOpenMVS_USE_OPENGL=OFF', '-DOpenMVS_USE_BREAKPAD=OFF',
                 '-DOpenMVS_USE_CERES=OFF', '-DOpenMVS_USE_PYTHON=OFF', '-DOpenMVS_ENABLE_TESTS=OFF',
                 '-DENABLE_SSE3=OFF', '-DENABLE_SSSE3=OFF', '-DENABLE_SSE41=OFF', '-DENABLE_SSE42=OFF',
                 '-DENABLE_AVX=OFF', '-DENABLE_AVX2=OFF']
    else:
        python = prefix / 'bin/python'
        if not python.is_file():
            raise ScaffoldError('The OpenSfM host prefix must contain Python')
        args += [f'-DPYTHON_EXECUTABLE={python}', '-DOPENSFM_BUILD_TESTS=OFF', '-DPYBIND11_TEST=OFF']
    run(args, cwd=source, env=env)
    if name == 'opensfm-odm':
        cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
        lines = set(cache.splitlines())
        for line in ('OPENSFM_BUILD_TESTS:BOOL=OFF', 'PYBIND11_TEST:BOOL=OFF'):
            if line not in lines:
                raise ScaffoldError(f'Unexpected OpenSfM CMake configuration: {line}')
        if not any(line in lines for line in ('FETCHCONTENT_FULLY_DISCONNECTED:UNINITIALIZED=ON',
                                               'FETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON')):
            raise ScaffoldError('OpenSfM FetchContent is not disconnected')
    build_command = ['cmake', '--build', str(build)]
    if name == 'openmvs-odm':
        build_command += ['--target', 'ReconstructMesh']
    run([*build_command, '--parallel', '2'], cwd=source, env=env)

    bindir = prefix / 'bin'
    bindir.mkdir(parents=True, exist_ok=True)
    share = prefix / 'share/odm-conda' / name
    share.mkdir(parents=True, exist_ok=True)
    license_dir = prefix / 'share/licenses' / name
    license_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'LICENSE', license_dir / 'packaging-MIT.txt')
    shutil.copy2(source / 'LICENSE', license_dir / 'upstream-LICENSE.txt')
    (share / 'SOURCE.txt').write_text('LOCAL RESEARCH ONLY: upstream sources and assets have not been cleared for redistribution.\n', encoding='utf-8')
    if name == 'openmvs-odm':
        shutil.copy2(build / 'bin/ReconstructMesh', bindir / 'ReconstructMesh')
        for filename in ('functional_test.py', 'openmvs_synthetic_fixture.py', 'openmvs_pointcloud_fixture.py', 'texrecon_fixture.py'):
            shutil.copy2(ROOT / 'scripts' / filename, share / filename)
    else:
        python = prefix / 'bin/python'
        lib = Path(subprocess.check_output([str(python), '-c', 'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
        if not lib.resolve().is_relative_to(prefix):
            raise ScaffoldError('Host Python site-packages is outside the host prefix')
        package = source / 'opensfm'
        expected = ('pygeo', 'pygeometry', 'pyrobust', 'pybundle', 'pyfeatures', 'pydense', 'pysfm', 'pymap')
        for module in expected:
            if len(list(package.glob(module + '.*.so'))) != 1:
                raise ScaffoldError(f'OpenSfM native module missing or ambiguous: {module}')
        lib.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package, lib / 'opensfm', ignore=shutil.ignore_patterns('src', 'test', '__pycache__', '*.pyc'))
        for filename in ('opensfm_fixture.py', 'opensfm_assets_fixture.py'):
            shutil.copy2(ROOT / 'scripts' / filename, share / filename)
        shutil.copy2(source / 'bin/opensfm_main.py', share / 'opensfm_main.py')
        launcher = bindir / 'opensfm'
        launcher.write_text('#!/usr/bin/env bash\nset -e\nDIR="$(cd "$(dirname "$0")" && pwd)"\nexec "$DIR/python" "$DIR/../share/odm-conda/opensfm-odm/opensfm_main.py" "$@"\n', encoding='utf-8')
        launcher.chmod(0o755)
        shutil.copy2(source / 'bin/opensfm_run_all', bindir / 'opensfm_run_all')
        for rel, dest in [('opensfm/src/third_party/pybind11/LICENSE', 'pybind11-LICENSE.txt'),
                          ('opensfm/src/third_party/akaze/LICENSE', 'akaze-LICENSE.txt'),
                          ('opensfm/src/third_party/vlfeat/COPYING', 'vlfeat-COPYING.txt'),
                          ('opensfm/data/sensor_data.readme.txt', 'sensor-data-notice.txt')]:
            shutil.copy2(source / rel, license_dir / dest)


if __name__ == '__main__':
    fail_cli(main)
