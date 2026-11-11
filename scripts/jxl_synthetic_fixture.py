#!/usr/bin/env python3
"""Exercise JPEG XL using generated pixels and metadata, not upstream samples.

This is bounded research coverage, not a replacement for all upstream tests or
an independent codec implementation.
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path


def pixels(mode: str, width: int, height: int) -> list:
    """Generate synthetic, non-constant 8-bit pixels without image inputs."""
    channels = {'L': 1, 'LA': 2, 'RGB': 3, 'RGBA': 4}[mode]
    result = []
    for y in range(height):
        for x in range(width):
            sample = tuple((x * 29 + y * 47 + channel * 61) % 256 for channel in range(channels))
            result.append(sample[0] if channels == 1 else sample)
    return result


def run() -> None:
    import pillow_jxl  # noqa: F401 - registers the format
    from PIL import Image, ImageCms, UnidentifiedImageError

    for mode in ('L', 'LA', 'RGB', 'RGBA'):
        image = Image.new(mode, (17, 13))
        image.putdata(pixels(mode, *image.size))
        output = io.BytesIO()
        image.save(output, format='JXL', lossless=True, num_threads=1)
        assert output.getbuffer().nbytes > 0
        output.seek(0)
        with Image.open(output) as decoded:
            decoded.load()
            assert decoded.format == 'JXL' and decoded.size == image.size and decoded.mode == mode
            assert decoded.tobytes() == image.tobytes(), mode
            assert not decoded.is_animated and decoded.n_frames == 1
        print(f'PASS: generated {mode} lossless pixels', flush=True)

    image = Image.new('RGB', (17, 13))
    image.putdata(pixels('RGB', *image.size))
    exif = Image.Exif()
    exif[270] = 'synthetic-odm-jxl-test'
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    encoded = io.BytesIO()
    image.save(encoded, format='JXL', lossless=True, use_container=True,
               exif=exif.tobytes(), icc_profile=icc, num_threads=1)
    encoded.seek(0)
    with Image.open(encoded) as decoded:
        decoded.load()
        assert decoded.size == image.size and decoded.tobytes() == image.tobytes()
        assert decoded.getexif().get(270) == 'synthetic-odm-jxl-test'
        # Profile support and transformations differ between codec versions;
        # verify a valid nonempty generated output profile, not byte identity.
        assert decoded.info.get('icc_profile')
    print('PASS: synthetic EXIF and ICC profile present', flush=True)

    with tempfile.TemporaryDirectory(prefix='jxl-synthetic-') as tmp:
        jpeg = Path(tmp)/'synthetic.jpg'
        image.save(jpeg, format='JPEG', quality=95, exif=exif.tobytes())
        with Image.open(jpeg) as original:
            original.load()
            expected, size = original.tobytes(), original.size
            jxl = Path(tmp)/'synthetic.jxl'
            original.save(jxl, format='JXL', lossless_jpeg=True, num_threads=1)
        with Image.open(jxl) as decoded:
            decoded.load()
            assert decoded.size == size and decoded.mode == 'RGB'
            assert decoded.tobytes() == expected
            assert decoded.getexif().get(270) == 'synthetic-odm-jxl-test'
    print('PASS: generated JPEG reconstruction pixels and EXIF', flush=True)

    lossy = io.BytesIO()
    image.save(lossy, format='JXL', quality=80, num_threads=1)
    lossy.seek(0)
    with Image.open(lossy) as decoded:
        decoded.load()
        assert decoded.size == image.size and decoded.mode == 'RGB'
    print('PASS: generated lossy RGB decode dimensions and mode', flush=True)

    try:
        Image.open(io.BytesIO(b'not-a-jxl-file')).load()
    except (UnidentifiedImageError, OSError, ValueError):
        pass
    else:
        raise AssertionError('Invalid input was accepted as an image')
    print('PASS: invalid image rejected', flush=True)


if __name__ == '__main__':
    run()
