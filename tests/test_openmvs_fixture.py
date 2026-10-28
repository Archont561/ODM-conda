from pathlib import Path

import pytest


def test_openmvs_fixture_rejects_program_that_does_not_produce_mesh(tmp_path):
    from openmvs_fixture import test_openmvs

    with pytest.raises(AssertionError, match='Missing output mesh'):
        test_openmvs(Path('/bin/true'), tmp_path)


def test_openmvs_fixture_rejects_truncated_binary_mesh(tmp_path):
    from openmvs_fixture import validate_mesh

    mesh = tmp_path / 'broken.ply'
    mesh.write_bytes(b'ply\nformat binary_little_endian 1.0\nelement vertex 7\n'
                     b'property float32 x\nproperty float32 y\nproperty float32 z\n'
                     b'element face 10\nproperty list uint8 uint32 vertex_indices\nend_header\n' + b'\0')
    with pytest.raises(AssertionError, match='Invalid mesh length'):
        validate_mesh(mesh)


def test_openmvs_fixture_rejects_invalid_triangle_indices(tmp_path):
    import struct
    from openmvs_fixture import validate_mesh

    mesh = tmp_path / 'bad-indices.ply'
    header = (b'ply\nformat binary_little_endian 1.0\nelement vertex 7\n'
              b'property float32 x\nproperty float32 y\nproperty float32 z\n'
              b'element face 10\nproperty list uint8 uint32 vertex_indices\nend_header\n')
    mesh.write_bytes(header + struct.pack('<3f', 0, 0, 0) * 7 + struct.pack('<B3I', 3, 0, 1, 7) * 10)
    with pytest.raises(AssertionError, match='Invalid triangle'):
        validate_mesh(mesh)
