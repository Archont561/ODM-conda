#!/usr/bin/env python3
"""Compare plugin-encoded synthetic files with a separate jxl-oxide decoder.

Pass the path to a trusted jxl-oxide CLI. No samples are downloaded or retained.
This is limited interoperability testing, not a complete conformance suite.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


def pixels(mode: str, width: int, height: int) -> list:
    channels = {'L': 1, 'LA': 2, 'RGB': 3, 'RGBA': 4}[mode]
    values = []
    for y in range(height):
        for x in range(width):
            sample = tuple((x * 29 + y * 47 + c * 61) % 256 for c in range(channels))
            values.append(sample[0] if channels == 1 else sample)
    return values


def decode(decoder: Path, source: Path, output: Path, *, jpeg: bool = False) -> None:
    command = [str(decoder), '--quiet', 'decode', str(source), '--output', str(output),
               '--output-format', 'jpeg' if jpeg else 'png8']
    subprocess.run(command, check=True, timeout=60)
    if not output.is_file() or not output.stat().st_size:
        raise AssertionError('Independent decoder produced no output')


def run(decoder: Path) -> None:
    import pillow_jxl  # noqa: F401
    from PIL import Image

    decoder = decoder.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='odm-jxl-interop-') as tmp:
        root = Path(tmp)
        for mode in ('L', 'LA', 'RGB', 'RGBA'):
            image = Image.new(mode, (17, 13))
            image.putdata(pixels(mode, *image.size))
            jxl, png = root/f'{mode}.jxl', root/f'{mode}.png'
            image.save(jxl, format='JXL', lossless=True, num_threads=1)
            decode(decoder, jxl, png)
            with Image.open(png) as result:
                result.load()
                if result.size != image.size or result.mode != mode or result.tobytes() != image.tobytes():
                    raise AssertionError(f'Independent decoder lossless mismatch: {mode}')
            print(f'PASS: independent decoder {mode} lossless', flush=True)

        image = Image.new('RGB', (17, 13))
        image.putdata(pixels('RGB', *image.size))
        jpeg, jxl, recovered = root/'original.jpg', root/'jpeg.jxl', root/'recovered.jpg'
        image.save(jpeg, format='JPEG', quality=95)
        with Image.open(jpeg) as source:
            source.save(jxl, format='JXL', lossless_jpeg=True, num_threads=1)
        decode(decoder, jxl, recovered, jpeg=True)
        if recovered.read_bytes() != jpeg.read_bytes():
            raise AssertionError('Independent JPEG reconstruction differs byte-for-byte')
        print('PASS: independent decoder reconstructed original JPEG bytes', flush=True)

        jxl, png = root/'lossy.jxl', root/'lossy.png'
        image.save(jxl, format='JXL', quality=80, num_threads=1)
        decode(decoder, jxl, png)
        with Image.open(jxl) as plugin, Image.open(png) as independent:
            plugin.load(); independent.load()
            if plugin.size != independent.size or plugin.mode != independent.mode:
                raise AssertionError('Independent lossy dimensions or mode mismatch')
            differences = [abs(a-b) for a, b in zip(plugin.tobytes(), independent.tobytes())]
            if not differences or max(differences) > 2:
                raise AssertionError(f'Independent lossy pixel mismatch: max {max(differences, default=-1)}')
        print('PASS: independent lossy pixels within 2/255 per channel', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decoder', required=True, type=Path)
    run(parser.parse_args().decoder)


if __name__ == '__main__':
    main()
