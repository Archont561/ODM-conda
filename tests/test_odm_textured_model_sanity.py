import pytest

from odm_textured_model_sanity import validate


def test_valid_textured_triangle_and_invalid_data(tmp_path):
    model = tmp_path/'model.obj'
    obj = ('mtllib model.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\n'
           'vt 0 0\nvt 1 0\nvt 0 1\nf 1/1 2/2 3/3\n')
    (tmp_path/'model.mtl').write_text('newmtl a\nmap_Kd texture.png\n')
    (tmp_path/'texture.png').write_bytes(b'x'*20)
    model.write_text(obj)
    assert validate(model)['triangles'] == 1
    model.write_text(obj.replace('v 0 0 0', 'v nan 0 0'))
    with pytest.raises(ValueError, match='coordinate'):
        validate(model)
    model.write_text(obj.replace('3/3', '4/3'))
    with pytest.raises(ValueError, match='index'):
        validate(model)
    model.write_text(obj)
    (tmp_path/'model.mtl').write_text('map_Kd ../secret\n')
    with pytest.raises(ValueError, match='Unsafe'):
        validate(model)
