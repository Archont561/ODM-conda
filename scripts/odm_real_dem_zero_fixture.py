#!/usr/bin/env python3
"""Inject a zero patch into copied, real-derived DEMs; never alter the inputs."""
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import rowcol, xy
from rasterio.warp import reproject, Resampling
from scipy.ndimage import binary_erosion


def run(prefix, app, inputs):
    if len(inputs) != 2:
        raise ValueError('Exactly two input DEMs required')
    os.environ['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    sys.path.insert(0, str(app))
    from opendm.dem.merge import euclidean_merge_dems
    with tempfile.TemporaryDirectory(prefix='odm-real-zero-') as temp:
        root = Path(temp)
        datasets = [rasterio.open(p) for p in inputs]
        try:
            first, second = datasets
            a = first.read(1); b = second.read(1)
            if first.crs is None or first.crs != second.crs:
                raise ValueError('Missing or unequal CRS')
            valid_a = (first.read_masks(1) > 0) & np.isfinite(a)
            valid_b = ((second.read_masks(1) > 0) & np.isfinite(b)).astype('uint8')
            mapped = np.zeros(a.shape, dtype='uint8')
            reproject(valid_b, mapped, src_transform=second.transform, src_crs=second.crs,
                      dst_transform=first.transform, dst_crs=first.crs,
                      resampling=Resampling.nearest, src_nodata=0, dst_nodata=0)
            safe = binary_erosion(valid_a & (mapped == 0), structure=np.ones((32, 32), dtype=bool))
            positions = np.argwhere(safe)
            if not len(positions): raise ValueError('No safely exclusive interior available')
            r, c = (int(v) for v in positions[len(positions)//2])
            patch = a[r-4:r+4, c-4:c+4]
            if patch.shape != (8, 8) or not np.all(np.isfinite(patch)) or np.any(patch == 0):
                raise ValueError('Invalid patch selection')
            original_range = [float(patch.min()), float(patch.max())]
            modified = a.copy(); modified[r-4:r+4, c-4:c+4] = 0
            original_paths, modified_paths = [], []
            for group, first_data in [('original', a), ('modified', modified)]:
                paths = []
                for i, (src, data) in enumerate(((first, first_data), (second, b))):
                    path = root / f'{group}-{i}.tif'
                    with rasterio.open(path, 'w', **src.profile) as dst: dst.write(data, 1)
                    paths.append(str(path))
                if group == 'original': original_paths = paths
                else: modified_paths = paths
            original = root / 'original-merged.tif'; changed = root / 'changed-merged.tif'
            euclidean_merge_dems(original_paths, str(original), {'TILED': 'NO'})
            euclidean_merge_dems(modified_paths, str(changed), {'TILED': 'NO'})
            with rasterio.open(original) as orig, rasterio.open(changed) as out:
                if orig.shape != out.shape or orig.transform != out.transform or orig.crs != out.crs:
                    raise AssertionError('Counterfactual output geometry changed')
                coords = [xy(first.transform, rr, cc) for rr in range(r-4,r+4) for cc in range(c-4,c+4)]
                positions = [rowcol(out.transform, x, y) for x,y in coords]
                if len(set(positions)) != 64: raise AssertionError('Output does not preserve distinct patch pixels')
                aa = orig.read(1); bb = out.read(1)
                before = np.array([aa[rr,cc] for rr,cc in positions]); after = np.array([bb[rr,cc] for rr,cc in positions])
                if not np.all(np.isfinite(before)) or np.any(before == orig.nodata) or np.any(before == 0):
                    raise AssertionError('Original output patch was not valid and nonzero')
                if not np.all(after == 0): raise AssertionError('Real-derived zero patch lost in merge')
                if not np.all(out.read_masks(1)[tuple(np.array(positions).T)] > 0):
                    raise AssertionError('Zero patch is marked invalid')
                return {'patch_pixels': 64, 'preserved_zero_pixels': int(np.count_nonzero(after == 0)),
                        'original_patch_range': original_range,
                        'original_output_range': [float(before.min()), float(before.max())],
                        'output_shape': list(out.shape), 'input_count': len(inputs),
                        'intervention': '8x8 zero patch in an exclusive interior region of copied real-derived DEM; original unmodified'}
        finally:
            for dataset in datasets: dataset.close()


if __name__ == '__main__':
    print('FIXTURE_JSON '+json.dumps(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3:]), sort_keys=True), flush=True)
