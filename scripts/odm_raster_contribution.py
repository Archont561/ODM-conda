#!/usr/bin/env python3
"""Sample raster coverage, exclusive source matches and overlap gradients.

A diagnostic, not proof of full-resolution contribution, seam quality or accuracy.
"""
import argparse
import json
import numpy as np


def summarize(inputs, masks, output, outmask, tolerance):
    if len(inputs) != 2 or len(masks) != 2 or any(a.shape != output.shape for a in inputs):
        raise ValueError('Expected two matching rasters')
    if any(mask.shape != output.shape[1:] for mask in [*masks, outmask]):
        raise ValueError('Invalid mask shape')
    finite = np.isfinite(output).all(axis=0)
    usable = outmask & finite
    overlap = masks[0] & masks[1] & usable
    results=[]
    for i in range(2):
        exclusive=masks[i] & ~masks[1-i] & usable & np.isfinite(inputs[i]).all(axis=0)
        diff=np.max(np.abs(inputs[i][:,exclusive].astype('float64')-output[:,exclusive].astype('float64')),axis=0)
        results.append({'exclusive_samples':int(exclusive.sum()),
                        'within_tolerance_fraction':float(np.mean(diff<=tolerance)) if diff.size else None,
                        'median_absolute_max_band_difference':float(np.median(diff)) if diff.size else None})
    # Adjacent differences sampled within overlapping source coverage; not a
    # direct seam detector and sensitive to real image/terrain texture.
    values=output.astype('float64')
    samples=[]
    for axis in (1, 2):
        a=np.take(overlap, range(overlap.shape[axis-1]-1), axis=axis-1)
        b=np.take(overlap, range(1, overlap.shape[axis-1]), axis=axis-1)
        delta=np.max(np.abs(np.diff(values,axis=axis)),axis=0)
        samples.extend(delta[a & b].tolist())
    return {'inputs':results,'overlap_output_samples':int(overlap.sum()),
            'output_valid_samples':int(usable.sum()), 'tolerance':tolerance,
            'overlap_adjacent_max_band_p95':float(np.percentile(samples,95)) if samples else None}


def inspect(output_path, paths, kind, max_side=512):
    import rasterio
    from affine import Affine
    from rasterio.enums import Resampling
    from rasterio.vrt import WarpedVRT
    from contextlib import ExitStack
    if len(paths)!=2 or kind not in ('ortho','dem'):
        raise ValueError('Expected exactly two inputs and known raster kind')
    with ExitStack() as stack:
        dst=stack.enter_context(rasterio.open(output_path))
        if not dst.crs or dst.width<1 or dst.height<1 or (kind=='ortho' and dst.count<3):
            raise ValueError('Invalid merged raster')
        scale=max(1, max(dst.width,dst.height)/max_side)
        width=max(1,round(dst.width/scale));height=max(1,round(dst.height/scale))
        transform=dst.transform*Affine.scale(dst.width/width,dst.height/height)
        def warped(path):
            src=stack.enter_context(rasterio.open(path))
            if not src.crs or src.crs != dst.crs or (kind=='ortho' and src.count<3):
                raise ValueError('Source CRS or band mismatch')
            vrt=stack.enter_context(WarpedVRT(src,crs=dst.crs,transform=transform,width=width,height=height,resampling=Resampling.nearest))
            bands=[1,2,3] if kind=='ortho' else [1]
            return vrt.read(bands), vrt.dataset_mask()>0
        out,outmask=warped(output_path)
        sources=[warped(path) for path in paths]
        result=summarize([x[0] for x in sources],[x[1] for x in sources],out,outmask,12 if kind=='ortho' else .10)
        result.update({'kind':kind,'grid':[width,height], 'method':'nearest-neighbor samples on merged grid',
                       'limitations':'Sampling only; overlaps and thresholds do not prove visual, geometric or seam quality.'})
        return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=('ortho','dem'),required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('inputs',nargs=2)
    args=parser.parse_args()
    print(json.dumps(inspect(args.output,args.inputs,args.kind),sort_keys=True))


if __name__=='__main__':
    main()
