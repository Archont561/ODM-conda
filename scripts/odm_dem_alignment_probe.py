#!/usr/bin/env python3
"""Diagnostic of a supplied ODM dem/merge.py with precomputed distance maps.

Requires numpy, scipy and rasterio. Supply a trusted, pinned ODM source/app path.
This is a scoped algorithm probe, not an installed-package or GDAL proximity test.
"""
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from scipy.ndimage import distance_transform_edt


def load_merge(app):
    # Isolate the merge algorithm; precomputed maps deliberately replace the
    # heavier commands module. Never mix with another loaded opendm instance.
    if any(name == 'opendm' or name.startswith('opendm.') for name in sys.modules):
        raise RuntimeError('run probe in a fresh Python process')
    package = types.ModuleType('opendm'); package.__path__ = [str(app / 'opendm')]
    dem = types.ModuleType('opendm.dem'); dem.__path__ = [str(app / 'opendm/dem')]
    system = types.ModuleType('opendm.system')
    log = types.ModuleType('opendm.log'); log.ODM_INFO = lambda *_: None; log.ODM_WARNING = lambda *_: None
    io = types.ModuleType('opendm.io'); io.file_exists = os.path.isfile
    io.related_file_path = lambda path, postfix, replace_base=None: str(Path(path).with_suffix('')) + postfix + '.tif'
    commands = types.ModuleType('opendm.dem.commands')
    commands.compute_euclidean_map = lambda source, output, overwrite=False: output if os.path.isfile(output) else None
    sys.modules.update({'opendm': package, 'opendm.dem': dem, 'opendm.system': system,
                        'opendm.log': log, 'opendm.io': io, 'opendm.dem.commands': commands})
    spec = importlib.util.spec_from_file_location('odm_probe_merge', app / 'opendm/dem/merge.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.euclidean_merge_dems


def run(app):
    merge = load_merge(app)
    results = []
    with tempfile.TemporaryDirectory(prefix='odm-alignment-') as temp:
        root = Path(temp)
        for offset, nodata, values in [(8.0, -9999.0, (100.0, 200.0)),
                                        (8.25, -9999.0, (100.0, 200.0)),
                                        (8.75, -9999.0, (100.0, 200.0)),
                                        (8.0, -9999.0, (0.0, 200.0)),
                                        (8.0, 0.0, (100.0, 200.0)),
                                        (8.0, -9999.0, (100.0, -9999.0))]:
            paths = []; sources = []
            for i, value in enumerate(values):
                data = np.full((24, 24), value, dtype='float32')
                data[0, :] = data[-1, :] = nodata; data[:, 0] = data[:, -1] = nodata
                transform = from_origin(i * offset, 24, 1, 1)
                path = root / f'input-{i}.tif'; distance_path = root / f'input-{i}.euclideand.tif'
                profile = dict(driver='GTiff', width=24, height=24, count=1, dtype='float32',
                               nodata=nodata, crs='EPSG:32617', transform=transform)
                with rasterio.open(path, 'w', **profile) as dst: dst.write(data, 1)
                distance = distance_transform_edt(data != nodata).astype('float32')
                profile['nodata'] = 0
                with rasterio.open(distance_path, 'w', **profile) as dst: dst.write(distance, 1)
                sources.append((data, distance, transform)); paths.append(str(path))
            output = root / 'merged.tif'
            try:
                merge(paths, str(output), {'TILED': 'NO'})
                with rasterio.open(output) as src:
                    result = src.read(1); transform = src.transform; shape = src.shape
                weights = []; vals = []
                for data, distance, source_transform in sources:
                    d = np.full(shape, nodata, dtype='float32'); w = np.zeros(shape, dtype='float32')
                    reproject(data, d, src_transform=source_transform, src_crs='EPSG:32617', src_nodata=nodata,
                              dst_transform=transform, dst_crs='EPSG:32617', dst_nodata=nodata, resampling=Resampling.nearest)
                    reproject(distance, w, src_transform=source_transform, src_crs='EPSG:32617', src_nodata=0,
                              dst_transform=transform, dst_crs='EPSG:32617', dst_nodata=0, resampling=Resampling.nearest)
                    weights.append(w); vals.append(np.where(d == nodata, 0, d))
                total = weights[0] + weights[1]; valid = total > 0
                expected = np.full(shape, nodata, dtype='float32')
                np.divide(vals[0]*weights[0] + vals[1]*weights[1], total, out=expected, where=valid)
                different = ~np.isclose(result, expected, atol=1e-4, rtol=0)
                results.append({'offset': offset, 'nodata': nodata, 'values': list(values),
                                'shape': list(shape), 'expected_valid': int(valid.sum()),
                                'output_valid': int((result != nodata).sum()), 'different_pixels': int(different.sum())})
            except Exception as exc:
                results.append({'offset': offset, 'nodata': nodata, 'values': list(values),
                                'error': f'{type(exc).__name__}: {exc}'})
    return results


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve()), sort_keys=True))
