#!/usr/bin/env python3
"""Exercise installed ODM-generated proximity maps and their use in DEM merging."""
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy.ndimage import distance_transform_edt


def run(prefix, app):
    os.environ['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    sys.path.insert(0, str(app))
    from opendm.dem.commands import compute_euclidean_map
    from opendm.dem.merge import euclidean_merge_dems

    with tempfile.TemporaryDirectory(prefix='odm-distance-') as directory:
        root = Path(directory)
        nodata = -9999.0
        rasters, distances, arrays = [], [], []
        for index, value in enumerate((100.0, 200.0)):
            array = np.full((24, 24), value, dtype='float32')
            array[0, :] = nodata
            array[-1, :] = nodata
            array[:, 0] = nodata
            array[:, -1] = nodata
            # Different interior gaps make the overlapping weight field asymmetric.
            array[10:14, 15 if index == 0 else 8] = nodata
            path = root / f'dem-{index}.tif'
            distance = root / f'dem-{index}.euclideand.tif'
            with rasterio.open(path, 'w', driver='GTiff', width=24, height=24,
                               count=1, dtype='float32', nodata=nodata,
                               crs='EPSG:32617', transform=from_origin(index * 8, 24, 1, 1)) as dst:
                dst.write(array, 1)
            generated = compute_euclidean_map(str(path), str(distance), overwrite=True)
            if generated != str(distance) or not distance.is_file():
                raise AssertionError('ODM failed to generate distance map')
            with rasterio.open(distance) as src:
                actual = src.read(1)
                if src.crs.to_epsg() != 32617 or src.transform != from_origin(index * 8, 24, 1, 1):
                    raise AssertionError('distance map geometry mismatch')
            expected = distance_transform_edt(array != nodata)
            if not np.allclose(actual, expected, atol=1e-5):
                raise AssertionError(f'proximity mismatch: {np.max(np.abs(actual-expected))}')
            arrays.append(array); distances.append(actual); rasters.append(str(path))
        output = root / 'merged.tif'
        euclidean_merge_dems(rasters, str(output), {'TILED': 'NO'})
        with rasterio.open(output) as src:
            merged = src.read(1)
            if src.shape != (24, 32) or src.crs.to_epsg() != 32617:
                raise AssertionError('merge geometry mismatch')
        weights = np.zeros((2, 24, 32), dtype='float32')
        for i, (array, distance) in enumerate(zip(arrays, distances)):
            weights[i, :, i*8:i*8+24] = np.where(array != nodata, distance, 0)
        total = weights.sum(axis=0)
        valid = total > 0
        expected = np.zeros_like(total)
        np.divide(weights[0] * 100 + weights[1] * 200, total, out=expected, where=valid)
        if not np.allclose(merged[valid], expected[valid], atol=1e-4):
            raise AssertionError(f'weighted merge mismatch: {np.max(np.abs(merged[valid]-expected[valid]))}')
        if not np.all(merged[~valid] == nodata):
            raise AssertionError('unexpected output outside valid union')
        overlap = (weights[0] > 0) & (weights[1] > 0)
        uneven = overlap & (weights[0] != weights[1])
        if not uneven.any():
            raise AssertionError('no unequal-weight overlap')
        return {'shape': list(merged.shape), 'valid_pixels': int(valid.sum()),
                'overlap_pixels': int(overlap.sum()), 'unequal_weight_pixels': int(uneven.sum()),
                'nodata_pixels': int((~valid).sum()), 'max_distance': float(max(d.max() for d in distances)),
                'max_weighted_error': float(np.max(np.abs(merged[valid] - expected[valid])))}


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()), sort_keys=True))
