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


def test_dense_ply_validation_rejects_bad_and_accepts_bounded_fixture(tmp_path):
    import struct
    from openmvs_dense_dataset_fixture import validate_dense_ply

    path = tmp_path/'cloud.ply'
    header = b'ply\nformat binary_little_endian 1.0\nelement vertex 100\nend_header\n'
    path.write_bytes(header + struct.pack('<3f', 1, 2, 3)*100)
    assert validate_dense_ply(path) == 100
    path.write_bytes(header + struct.pack('<3f', float('nan'), 2, 3)*100)
    with pytest.raises(ValueError, match='nonfinite'):
        validate_dense_ply(path)
    path.write_bytes(header + b'broken')
    with pytest.raises(ValueError, match='Truncated'):
        validate_dense_ply(path)


def test_dense_evidence_is_bounded():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/openmvs-dense-research-evidence.json').read_text())
    assert data['dense_point_count'] == 28116
    assert 'not full ODM' in data['scope']
    assert 'discarded' in data['outputs']


def test_cpu_compat_patch_and_evidence():
    import json
    from pathlib import Path
    from common import sha256
    root = Path(__file__).resolve().parents[1]
    patch = root/'research/recipes/openmvs-dense-research/patches/odm-cpu-option.patch'
    assert sha256(patch) == '4ffb4d97b9373155194275994709cabfe900e1deff8b1d6950bc160f50029953'
    data = json.loads((root/'research/openmvs-dense-cpucompat-evidence.json').read_text())
    assert data['odm_stage']['overlay'] is True
    assert data['odm_stage']['images'] == 35
    assert 'scene_dense_dense_filtered.ply' in data['odm_stage']['outputs']
    assert data['cli_policy'] == 'accept only --cuda-device -2; reject -1 and 0; CPU only'
    assert 'not full ODM' in data['scope']
