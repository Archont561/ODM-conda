#!/usr/bin/env python3
"""Bounded GDAL metadata/statistics checks; not geographic or visual validation."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from common import ScaffoldError, fail_cli


def validate(info: dict) -> dict:
    size = info.get('size')
    if not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or v <= 0 for v in size):
        raise ScaffoldError('Invalid raster dimensions')
    transform = info.get('geoTransform')
    if not isinstance(transform, list) or len(transform) != 6 or any(type(v) not in (int,float) or not math.isfinite(v) for v in transform):
        raise ScaffoldError('Invalid geotransform')
    determinant = transform[1]*transform[5]-transform[2]*transform[4]
    if not math.isfinite(determinant) or determinant == 0:
        raise ScaffoldError('Degenerate geotransform')
    crs = info.get('coordinateSystem', {}).get('wkt')
    if not isinstance(crs, str) or not crs.strip():
        raise ScaffoldError('Missing raster CRS')
    bands = info.get('bands')
    if not isinstance(bands,list) or len(bands)<3:
        raise ScaffoldError('Expected at least three raster bands')
    results=[]
    for band in bands:
        stats = [band.get(key) for key in ('minimum','maximum','mean','stdDev')]
        if any(type(x) not in (int,float) or not math.isfinite(x) for x in stats):
            raise ScaffoldError('Missing or non-finite raster statistics')
        low,high,mean,std=stats
        if low>high or not low<=mean<=high or std<0:
            raise ScaffoldError('Invalid raster statistics')
        if band.get('type') == 'Byte' and (low < 0 or high > 255):
            raise ScaffoldError('Out-of-range Byte raster statistics')
        results.append({'type':band.get('type'), 'color':band.get('colorInterpretation'), 'minimum':low, 'maximum':high, 'mean':mean, 'stdDev':std})
    return {'scope':'Metadata and summary statistics only; not visual quality, geographic accuracy or dataset rights validation.', 'size':size, 'geoTransform':transform, 'crs_wkt':crs, 'bands':results}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raster',type=Path)
    args=parser.parse_args()
    if not args.raster.is_file():
        raise ScaffoldError('Missing raster')
    output=subprocess.run(['gdalinfo','-json','-stats',str(args.raster.resolve())],text=True,capture_output=True,check=True)
    print(json.dumps(validate(json.loads(output.stdout)),sort_keys=True,indent=2))


if __name__=='__main__':
    fail_cli(main)
