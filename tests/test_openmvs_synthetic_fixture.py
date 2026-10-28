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
