import pytest

from common import ScaffoldError
from openmvs_dense_link_map import verify_dense_link_map


def test_dense_link_map_requires_dense_input_and_rejects_restricted(tmp_path):
    path = tmp_path/'link.map'
    base = 'Memory Configuration Linker script and memory map libMVS.a libMath.a DensifyPointCloud.cpp.o OUTPUT('
    path.write_text(base)
    with pytest.raises(ScaffoldError, match='dense implementation'):
        verify_dense_link_map(path, 'DensifyPointCloud')
    path.write_text(base + ' SceneDensify.cpp.o')
    assert len(verify_dense_link_map(path, 'DensifyPointCloud')) == 64
    path.write_text(base + ' SceneDensify.cpp.o TRWS/solver.o')
    with pytest.raises(ScaffoldError, match='Restricted'):
        verify_dense_link_map(path, 'DensifyPointCloud')


def test_mesh_link_map_requires_reconstruction(tmp_path):
    path = tmp_path/'link.map'
    path.write_text('Memory Configuration Linker script and memory map libMVS.a libMath.a ReconstructMesh.cpp.o OUTPUT(')
    with pytest.raises(ScaffoldError, match='mesh implementation'):
        verify_dense_link_map(path, 'ReconstructMesh')
    path.write_text(path.read_text() + ' SceneReconstruct.cpp.o')
    assert len(verify_dense_link_map(path, 'ReconstructMesh')) == 64
