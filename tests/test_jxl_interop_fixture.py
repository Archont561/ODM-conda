from pathlib import Path

import pytest

from jxl_interop_fixture import decode, pixels
from jxl_synthetic_fixture import pixels as existing_pixels


@pytest.mark.parametrize('mode', ['L', 'LA', 'RGB', 'RGBA'])
def test_pixels_match_existing_fixture(mode):
    assert pixels(mode, 17, 13) == existing_pixels(mode, 17, 13)


def test_decoder_must_create_nonempty_output(tmp_path, monkeypatch):
    import jxl_interop_fixture as module
    calls = []
    monkeypatch.setattr(module.subprocess, 'run', lambda command, **kwargs: calls.append((command, kwargs)))
    output = tmp_path/'out.png'
    with pytest.raises(AssertionError, match='no output'):
        decode(Path('/tool'), tmp_path/'source.jxl', output)
    output.write_bytes(b'x')
    decode(Path('/tool'), tmp_path/'source.jxl', output, jpeg=True)
    assert calls[-1][0][-1] == 'jpeg'
    assert calls[-1][1] == {'check': True, 'timeout': 60}
