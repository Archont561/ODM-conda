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


@pytest.mark.parametrize('encoding,scalar_views', [('ascii', False), ('binary_little_endian', False),
                                                    ('binary_big_endian', True)])
def test_visible_cloud_variants_encode_explicit_ids(tmp_path, encoding, scalar_views):
    import struct
    from openmvs_synthetic_fixture import generate_visible_cloud

    cloud = generate_visible_cloud(tmp_path / 'views.ply', encoding=encoding, scalar_views=scalar_views)
    header, body = cloud.read_bytes().split(b'end_header\n', 1)
    assert f'format {encoding} 1.0'.encode() in header
    assert (b'property uchar views\n' in header) == scalar_views
    assert b'property list uchar uint view_indices\n' in header
    if encoding == 'ascii':
        assert len(body.splitlines()) == 400
        assert body.splitlines()[0].split()[-3:] == [b'2', b'0', b'1']
    else:
        order = '<' if encoding == 'binary_little_endian' else '>'
        layout = order + ('fffBBII' if scalar_views else 'fffBII')
        size = struct.calcsize(layout)
        assert len(body) == 400 * size
        assert struct.unpack_from(layout, body)[-3:] == (2, 0, 1)


def test_big_endian_guard_rejects_false_success(tmp_path):
    from openmvs_synthetic_fixture import check_big_endian_rejected

    with pytest.raises(AssertionError, match='Expected clean endian rejection'):
        check_big_endian_rejected(Path('/bin/true'), tmp_path)
