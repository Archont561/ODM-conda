"""Validation preflight must fail without installed executables."""
import pytest
from common import ScaffoldError
from validate_renderdem_laz import validate


def test_requires_renderdem_and_pdal(tmp_path):
    (tmp_path/'bin').mkdir()
    with pytest.raises(ScaffoldError, match='renderdem and the separate pdal CLI'):
        validate(tmp_path)
    (tmp_path/'bin/renderdem').write_text('')
    with pytest.raises(ScaffoldError, match='renderdem and the separate pdal CLI'):
        validate(tmp_path)


def test_laz_fixture_checks_pixels_and_restores_environment(tmp_path, monkeypatch):
    import os
    import struct
    import validate_renderdem_laz as module
    bindir=tmp_path/'bin'; bindir.mkdir()
    (bindir/'renderdem').write_text('')
    (bindir/'pdal').write_text('')
    original_path=os.environ.get('PATH')
    monkeypatch.setattr(module, 'test_renderdem', lambda _renderdem, work: (work/'points.las').write_bytes(b'LAS'))
    def execute(command, work):
        if command[0].endswith('/pdal'):
            header=bytearray(227); header[:4]=b'LASF'; header[104]=0x80
            (work/'points.laz').write_bytes(header)
        else:
            (work/'laz').mkdir()
            (work/'laz'/'result.tif').write_bytes(struct.pack('<4225f', *([42.0]*4225)))
    monkeypatch.setattr(module, 'execute', execute)
    monkeypatch.setattr(module, 'tiff_first_ifd', lambda _data: {256:(65,),257:(65,),258:(32,),339:(3,),259:(1,),33550:(1.,1.,0.),33922:(0.,0.,0.,0.,65.,0.),273:(0,),279:(65*65*4,)})
    module.validate(tmp_path)
    assert os.environ.get('PATH')==original_path


def test_uncompressed_laz_is_rejected_and_environment_restored(tmp_path, monkeypatch):
    import os
    import validate_renderdem_laz as module
    bindir=tmp_path/'bin'; bindir.mkdir()
    (bindir/'renderdem').write_text('')
    (bindir/'pdal').write_text('')
    original_path=os.environ.get('PATH')
    monkeypatch.setattr(module, 'test_renderdem', lambda _renderdem, work: (work/'points.las').write_bytes(b'LAS'))
    def execute(_command, work):
        header=bytearray(227); header[:4]=b'LASF'
        (work/'points.laz').write_bytes(header)
    monkeypatch.setattr(module, 'execute', execute)
    with pytest.raises(ScaffoldError, match='compressed'):
        module.validate(tmp_path)
    assert os.environ.get('PATH')==original_path
