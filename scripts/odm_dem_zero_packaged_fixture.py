#!/usr/bin/env python3
"""Check zero-height and nodata handling using installed ODM merge functions."""
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def run(prefix, app):
    os.environ['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    sys.path.insert(0, str(app))
    from opendm.dem.merge import euclidean_merge_dems
    with tempfile.TemporaryDirectory(prefix='odm-zero-height-') as temp:
        root = Path(temp)
        cases = {}
        for name, values, low_distance in [('zero', (0, 0), False),
                                            ('cancellation', (-100, 100), False),
                                            ('interpolated_zero', (0, 0), True)]:
            inputs = []
            for i, value in enumerate(values):
                data = np.full((8, 8), value, dtype='float32')
                data[0, :] = data[-1, :] = -9999
                data[:, 0] = data[:, -1] = -9999
                weights = np.where(data == -9999, 0, 10).astype('float32')
                if low_distance:
                    weights[4, 4] = 0.1
                path = root / f'{name}-{i}.tif'
                map_path = root / f'{name}-{i}.euclideand.tif'
                profile = {'driver': 'GTiff', 'width': 8, 'height': 8, 'count': 1,
                           'dtype': 'float32', 'nodata': -9999, 'crs': 'EPSG:32617',
                           'transform': from_origin(0, 8, 1, 1)}
                with rasterio.open(path, 'w', **profile) as dst: dst.write(data, 1)
                profile['nodata'] = 0
                with rasterio.open(map_path, 'w', **profile) as dst: dst.write(weights, 1)
                inputs.append(str(path))
            output = root / f'{name}-output.tif'
            euclidean_merge_dems(inputs, str(output), {'TILED': 'NO'})
            with rasterio.open(output) as src:
                actual = src.read(1)
                if src.shape != (8, 8) or src.crs.to_epsg() != 32617:
                    raise AssertionError('Unexpected output geometry')
            expected = np.full((8, 8), -9999, dtype='float32'); expected[1:-1, 1:-1] = 0
            if not np.array_equal(actual, expected):
                raise AssertionError(f'{name}: {np.count_nonzero(actual != expected)} incorrect pixels')
            cases[name] = {'valid_zero_pixels': int(np.count_nonzero(actual == 0)),
                           'nodata_pixels': int(np.count_nonzero(actual == -9999))}
        return cases


if __name__ == '__main__':
    print('FIXTURE_JSON ' + json.dumps(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()), sort_keys=True), flush=True)
