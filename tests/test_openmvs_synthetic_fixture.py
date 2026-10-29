from pathlib import Path

import pytest


def test_synthetic_reconstruction_rejects_no_output(tmp_path):
    from openmvs_synthetic_fixture import test_reconstruction

    with pytest.raises(AssertionError, match='Missing reconstruction output'):
        test_reconstruction(Path('/bin/true'), tmp_path)


def test_generated_scene_has_expected_version_and_images(tmp_path):
    from openmvs_synthetic_fixture import generate_scene

    scene = generate_scene(tmp_path)
    assert scene.read_bytes()[:12] == b'MVSI\x03\x00\x00\x00\x00\x00\x00\x00'
    assert (tmp_path / 'view0.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert (tmp_path / 'view1.png').is_file()


def test_separate_visible_pointcloud_requires_reconstructed_output(tmp_path):
    from openmvs_synthetic_fixture import test_separate_reconstruction

    with pytest.raises(AssertionError, match='Missing reconstruction output'):
        test_separate_reconstruction(Path('/bin/true'), tmp_path)


def test_visible_pointcloud_contains_camera_index_lists(tmp_path):
    from openmvs_synthetic_fixture import generate_visible_cloud

    cloud = generate_visible_cloud(tmp_path / 'views.ply')
    header, body = cloud.read_text().split('end_header\n')
    assert 'property list uchar uint view_indices\n' in header
    records = body.splitlines()
    assert len(records) == 400
    assert all(line.split()[-3:] == ['2', '0', '1'] for line in records)
