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


@pytest.mark.parametrize('with_counts', [False, True])
def test_missing_visibility_requires_an_explicit_clean_error(tmp_path, monkeypatch, with_counts):
    import openmvs_pointcloud_fixture as fixture

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'scene.mvs').write_bytes(b'scene')
    monkeypatch.setattr(fixture, 'DATASET_FILES', {'scene.mvs': hashlib.sha256(b'scene').hexdigest()})
    script = tmp_path / 'no-message'
    script.write_text('#!/bin/sh\nexit 1\n', encoding='ascii')
    script.chmod(0o755)
    working = tmp_path / 'working'
    working.mkdir()
    with pytest.raises(AssertionError, match='Missing visibility error'):
        fixture.test_missing_visibility(script, source, working, with_view_counts=with_counts)
    cloud = (working / 'no-views.ply').read_text(encoding='ascii')
    assert ('property uchar views\n' in cloud) == with_counts


@pytest.mark.parametrize('with_counts', [False, True])
def test_missing_visibility_accepts_clean_diagnostic(tmp_path, monkeypatch, with_counts):
    import openmvs_pointcloud_fixture as fixture

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'scene.mvs').write_bytes(b'scene')
    monkeypatch.setattr(fixture, 'DATASET_FILES', {'scene.mvs': hashlib.sha256(b'scene').hexdigest()})
    script = tmp_path / 'reject'
    script.write_text('#!/bin/sh\necho "error: point cloud requires per-point camera visibility"\nexit 1\n', encoding='ascii')
    script.chmod(0o755)
    working = tmp_path / 'working'
    working.mkdir()
    fixture.test_missing_visibility(script, source, working, with_view_counts=with_counts)


def test_missing_visibility_rejects_a_signalled_process(tmp_path, monkeypatch):
    import subprocess
    import openmvs_pointcloud_fixture as fixture

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'scene.mvs').write_bytes(b'scene')
    monkeypatch.setattr(fixture, 'DATASET_FILES', {'scene.mvs': hashlib.sha256(b'scene').hexdigest()})
    monkeypatch.setattr(fixture.subprocess, 'run', lambda *args, **kwargs: subprocess.CompletedProcess(args[0], -11, '', ''))
    working = tmp_path / 'working'
    working.mkdir()
    with pytest.raises(AssertionError, match='Expected a clean error'):
        fixture.test_missing_visibility(Path('/bin/true'), source, working)
