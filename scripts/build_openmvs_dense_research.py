#!/usr/bin/env python3
"""Build dense-capable pinned OpenMVS for private research, not distribution."""
from __future__ import annotations

import os
import platform
import shlex
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, run, sha256
from openmvs_dense_link_map import verify_dense_link_map

PINNED = {
    'apps/DensifyPointCloud/CMakeLists.txt': '8c83b89f770db9935c5ec086e6637e2b1acad602bf16b282f4a4a99e776dba95',
    'apps/DensifyPointCloud/DensifyPointCloud.cpp': 'b3b0ed0685bf4e2940fa05302fae3e7ab13bb33e5d2945fe8731a223168ab6a3',
    'libs/MVS/SceneDensify.cpp': 'e629b39ec6a6943d9610bafd2e028191757fef21ada5151a4964d50747a35d9b',
    'apps/ReconstructMesh/ReconstructMesh.cpp': 'df9536d2f40eb11910bec63469550b198ec9dd5e73f9756aa7227e743748a410',
    'libs/MVS/PointCloud.cpp': '20b1bcf9695f83bfd7436728b32a51318b9f880e60410e642ba82c30054a154a',
    'libs/CMakeLists.txt': '1739176780c7cb6d3e1ebba33fb919c2ae094bd540151a4844027749fc379803',
    'apps/CMakeLists.txt': 'be2a6cce0578654ad3461cfced37d68b1cacea15a15dcdf23c80b57abe73b2da',
    'libs/Math/TetraFlow.h': 'dd3376a592b4c52321b8ab2130cfaadb0ed3b03980a0c7608ad9c98f73c2b380',
    'libs/MVS/SceneReconstruct.cpp': 'd0c564be0378d986e0194361920ab6799e7978b00a34aa0c0c611e411de1269a',
    'libs/MVS/CMakeLists.txt': '2deb822289b9a6d4320692c9ef0758f33cd0635547067fce47c24a849801f4f3',
}


def prepare_source(source: Path) -> None:
    source=Path(source)
    if source.is_symlink() or not source.is_dir(): raise ScaffoldError('Unsafe source tree')
    for name,digest in PINNED.items():
        path=source/name
        if path.is_symlink() or not path.is_file() or sha256(path)!=digest:
            raise ScaffoldError(f'Unexpected alternative source: {name}')
    for name in ('libs/Math/IBFS', 'libs/Math/TRWS'):
        path=source/name
        if path.exists() or path.is_symlink(): raise ScaffoldError(f'Restricted directory present: {name}')
    text=(source/'libs/MVS/SceneReconstruct.cpp').read_text()
    if 'typedef SEACAVE::TetraFlow maxflow_t;' not in text: raise ScaffoldError('Alternative solver missing')
    (source/'libs/CMakeLists.txt').write_text('ADD_SUBDIRECTORY(Common)\nADD_SUBDIRECTORY(Math)\nADD_SUBDIRECTORY(IO)\nADD_SUBDIRECTORY(MVS)\n')
    (source/'apps/CMakeLists.txt').write_text('ADD_SUBDIRECTORY(ReconstructMesh)\nADD_SUBDIRECTORY(DensifyPointCloud)\n')
    cmake=source/'libs/MVS/CMakeLists.txt'; text=cmake.read_text()
    old='LIST(REMOVE_ITEM LIBRARY_FILES_C "${PATH_PythonWrapper_cpp}")'
    new='LIST(REMOVE_ITEM LIBRARY_FILES_C "${PATH_PythonWrapper_cpp}"\n "${CMAKE_CURRENT_SOURCE_DIR}/SceneTexture.cpp"\n "${CMAKE_CURRENT_SOURCE_DIR}/SceneRefine.cpp")'
    if text.count(old)!=1: raise ScaffoldError('Unexpected MVS source list')
    cmake.write_text(text.replace(old,new))


def main() -> None:
    if os.environ.get('PKG_NAME')!='openmvs-dense-research' or platform.system()!='Linux' or platform.machine().lower() not in ('amd64','x86_64'):
        raise ScaffoldError('Only the linux-64 private research package is supported')
    if any(not os.environ.get(k) for k in ('PREFIX','BUILD_PREFIX','SRC_DIR')): raise ScaffoldError('Missing build environment')
    prefix, build_prefix, source=(Path(os.environ[k]).resolve() for k in ('PREFIX','BUILD_PREFIX','SRC_DIR'))
    if prefix in (build_prefix,source,ROOT,Path('/')) or source in (ROOT,Path('/')): raise ScaffoldError('Unsafe build paths')
    prepare_source(source)
    patch = ROOT/'research/recipes/openmvs-tetraflow-research/patches/visibility-ply.patch'
    run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(patch)], cwd=source)
    cpu_patch = ROOT/'research/recipes/openmvs-dense-research/patches/odm-cpu-option.patch'
    if cpu_patch.is_symlink() or not cpu_patch.is_file() or sha256(cpu_patch) != '4ffb4d97b9373155194275994709cabfe900e1deff8b1d6950bc160f50029953':
        raise ScaffoldError('Unexpected ODM CPU option patch')
    run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(cpu_patch)], cwd=source)
    env=os.environ.copy(); env['CONDA_PREFIX']=str(prefix); env['CMAKE_PREFIX_PATH']=str(prefix)
    build=source/'.research-build'; link_map=build/'ReconstructMesh-link.map'
    flags=f"{env.get('LDFLAGS','')} -Wl,-Map={link_map}"
    args=['cmake','-S',str(source),'-B',str(build),'-G','Ninja',*shlex.split(env.get('CMAKE_ARGS','')),
          '-DCMAKE_BUILD_TYPE=Release',f'-DCMAKE_PREFIX_PATH={prefix}',f'-DCMAKE_INSTALL_PREFIX={prefix}',
          '-DBUILD_SHARED_LIBS=OFF','-DBUILD_TESTING=OFF','-DFETCHCONTENT_FULLY_DISCONNECTED=ON',f'-DCMAKE_EXE_LINKER_FLAGS={flags}',
          f"-DCMAKE_CXX_FLAGS={env.get('CXXFLAGS','')} -march=x86-64 -mno-popcnt -DEIGEN_MPL2_ONLY",
          f"-DEIGEN3_INCLUDE_DIR={source/'_external/eigen'}", '-DOpenMVS_USE_CUDA=OFF',
          '-DOpenMVS_USE_BREAKPAD=OFF','-DOpenMVS_USE_CERES=OFF','-DOpenMVS_USE_PYTHON=OFF',
          '-DOpenMVS_USE_SIFTGPU=OFF','-DOpenMVS_ENABLE_TESTS=OFF','-DOpenMVS_USE_SSE=OFF']
    run(args,cwd=source,env=env)
    run(['cmake','--build',str(build),'--target','ReconstructMesh','--parallel','2'],cwd=source,env=env)
    digest=verify_dense_link_map(link_map, 'ReconstructMesh')
    run(['cmake','--build',str(build),'--target','DensifyPointCloud','--parallel','2'],cwd=source,env=env)
    dense_digest=verify_dense_link_map(link_map, 'DensifyPointCloud')
    print(f'PASS: dense named link inputs SHA256 {dense_digest}; no rights conclusion',flush=True)
    print(f'PASS: alternative link-map named input checks, SHA256 {digest}; no rights conclusion',flush=True)
    bindir=prefix/'bin'; bindir.mkdir(parents=True,exist_ok=True); shutil.copy2(build/'bin/ReconstructMesh',bindir/'ReconstructMesh'); shutil.copy2(build/'bin/DensifyPointCloud',bindir/'DensifyPointCloud')
    share=prefix/'share/odm-conda/openmvs-dense-research'; share.mkdir(parents=True,exist_ok=True)
    for name in ('openmvs_synthetic_fixture.py','openmvs_pointcloud_fixture.py','openmvs_fixture.py','texrecon_fixture.py','openmvs_tetraflow_weights_fixture.py','openmvs_odm_cleanup_fixture.py'):
        shutil.copy2(ROOT/'scripts'/name,share/name)
    (share/'SOURCE.txt').write_text('PRIVATE RESEARCH ONLY: rights and ODM compatibility unreviewed.\n')


if __name__ == '__main__': fail_cli(main)
