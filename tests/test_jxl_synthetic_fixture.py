import pytest
from jxl_synthetic_fixture import pixels


@pytest.mark.parametrize('mode,channels', [('L', 1), ('LA', 2), ('RGB', 3), ('RGBA', 4)])
def test_generated_pixels_are_deterministic_nonconstant_and_8bit(mode, channels):
    result = pixels(mode, 17, 13)
    assert len(result) == 221
    assert result == pixels(mode, 17, 13)
    values = [(p,) if channels == 1 else p for p in result]
    assert all(len(p) == channels and all(0 <= n <= 255 for n in p) for p in values)
    assert len(set(values)) > 1
