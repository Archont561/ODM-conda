#!/usr/bin/env python3
"""Test an untouched SRTM-format sample's zero values in overlapping crops.

Input is the independently hash-verified N10W110.hgt.zip rasterio test asset.
Zero encodings, especially over ocean, are not verified terrain observations.
"""
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

ARCHIVE_SHA256 = '7c668fd7868fbf8addcad0b1f993259d3d4f65f9f8990099e67e31fb1f595362'


def run(prefix, app, archive):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Unexpected SRTM-format archive hash')
    os.environ['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    sys.path.insert(0, str(app))
    from opendm.dem.merge import euclidean_merge_dems
    with tempfile.TemporaryDirectory(prefix='odm-srtm-overlap-') as temp:
        root = Path(temp)
        with zipfile.ZipFile(archive) as z:
            members = z.infolist()
            if len(members) != 1 or members[0].filename != 'N10W110.hgt' or members[0].file_size != 2884802:
                raise ValueError('Unexpected HGT archive contents')
            (root / 'N10W110.hgt').write_bytes(z.read(members[0]))
        with rasterio.open(root / 'N10W110.hgt') as src:
            if src.shape != (1201, 1201) or not src.crs or src.crs.to_epsg() != 4326:
                raise ValueError('Unexpected input geometry or CRS')
            window = Window(815, 730, 256, 256)
            sample = src.read(1, window=window)
            source_valid = src.read_masks(1, window=window) > 0
            transform = src.window_transform(window)
        if not source_valid.all() or not np.any(sample > 0) or not np.any(sample == 0):
            raise ValueError('Expected valid positive and zero samples')
        paths = []
        valid = np.zeros((2, 256, 256), dtype=bool)
        for i, offset in enumerate((0, 64)):
            # Add nodata borders, preserving every interior sample unchanged.
            data = sample[:, offset:offset+192].astype('float32')
            data[0, :] = data[-1, :] = -32768
            data[:, 0] = data[:, -1] = -32768
            valid[i, :, offset:offset+192] = data != -32768
            path = root / f'crop-{i}.tif'
            with rasterio.open(path, 'w', driver='GTiff', width=192, height=256,
                               count=1, dtype='float32', nodata=-32768, crs='EPSG:4326',
                               transform=transform * rasterio.Affine.translation(offset, 0)) as dst:
                dst.write(data, 1)
            paths.append(str(path))
        merged = root / 'merged.tif'
        euclidean_merge_dems(paths, str(merged), {'TILED': 'NO'})
        with rasterio.open(merged) as src:
            if src.shape != sample.shape or src.transform != transform or src.crs.to_epsg() != 4326:
                raise AssertionError('Unexpected merged geometry')
            result = src.read(1); output_valid = src.read_masks(1) > 0
        union = valid.any(axis=0); overlap = valid.all(axis=0)
        zeros = (sample == 0) & union; overlap_zeros = (sample == 0) & overlap
        positives = (sample > 0) & union
        if not np.array_equal(output_valid, union): raise AssertionError('Output coverage differs from union')
        if not np.allclose(result[union], sample[union], atol=1e-5, rtol=0):
            raise AssertionError('Merged value differs from identical overlapping sources')
        if not overlap_zeros.any() or not positives.any(): raise AssertionError('Missing overlap zero or positive values')
        return {'shape': list(sample.shape), 'valid_pixels': int(union.sum()),
                'zero_pixels': int(zeros.sum()), 'overlap_zero_pixels': int(overlap_zeros.sum()),
                'positive_pixels': int(positives.sum()), 'positive_max': int(sample[positives].max()),
                'max_abs_error': float(np.max(np.abs(result[union]-sample[union]))),
                'archive_sha256': ARCHIVE_SHA256}


if __name__ == '__main__':
    print('FIXTURE_JSON '+json.dumps(run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),Path(sys.argv[3]).resolve()),sort_keys=True),flush=True)
