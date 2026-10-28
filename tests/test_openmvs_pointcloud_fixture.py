import hashlib
import struct
from pathlib import Path

import pytest


def test_fixture_requires_matching_dataset(tmp_path, monkeypatch):
    import openmvs_pointcloud_fixture as fixture

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'scene.mvs').write_bytes(b'not the expected scene')
    monkeypatch.setattr(fixture, 'DATASET_FILES', {'scene.mvs': hashlib.sha256(b'original').hexdigest()})
    with pytest.raises(AssertionError, match='Dataset hash mismatch'):
        fixture.verify_dataset(source)


def test_fixture_rejects_success_without_reconstruction(tmp_path, monkeypatch):
    import openmvs_pointcloud_fixture as fixture

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'scene.mvs').write_bytes(b'scene')
    monkeypatch.setattr(fixture, 'DATASET_FILES', {'scene.mvs': hashlib.sha256(b'scene').hexdigest()})
    working = tmp_path / 'working'
    working.mkdir()
    with pytest.raises(AssertionError, match='Missing reconstruction output'):
        fixture.test_pointcloud(Path('/bin/true'), source, working)


def test_mesh_validator_rejects_invalid_triangle_indices(tmp_path):
    from openmvs_pointcloud_fixture import validate_mesh

    mesh = tmp_path / 'bad.ply'
    header = (b'ply\nformat binary_little_endian 1.0\nelement vertex 3\n'
              b'property float32 x\nproperty float32 y\nproperty float32 z\n'
              b'element face 1\nproperty list uint8 uint32 vertex_indices\nend_header\n')
    mesh.write_bytes(header + struct.pack('<3f', 0, 0, 0) * 3 + struct.pack('<B3I', 3, 0, 1, 3))
    with pytest.raises(AssertionError, match='Invalid triangle'):
        validate_mesh(mesh, min_vertices=3, min_faces=1)
