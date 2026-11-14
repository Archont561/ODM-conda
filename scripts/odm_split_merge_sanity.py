#!/usr/bin/env python3
"""Bounded private research validation of a PDAL LAS/LAZ merge, not accuracy proof."""
import csv
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

# These are the dimensions expected in the observed ODM split point clouds.
DIMENSIONS = ('X', 'Y', 'Z', 'Intensity', 'ReturnNumber', 'NumberOfReturns',
              'ScanDirectionFlag', 'EdgeOfFlightLine', 'Classification', 'Synthetic',
              'KeyPoint', 'Withheld', 'Overlap', 'ScanAngleRank', 'UserData',
              'PointSourceId', 'GpsTime', 'ScanChannel', 'Red', 'Green', 'Blue')


def compare_rows(inputs, output, tolerance=0.0011):
    """Compare concatenated input order and dimensions, allowing LAS quantization."""
    sentinel = object()
    import itertools
    count = 0
    for left, right in itertools.zip_longest(inputs, output, fillvalue=sentinel):
        if left is sentinel or right is sentinel:
            raise ValueError('Merged point count differs')
        for key in DIMENSIONS:
            a, b = float(left[key]), float(right[key])
            if not math.isfinite(a) or not math.isfinite(b):
                raise ValueError(f'Nonfinite {key}')
            if abs(a-b) > (tolerance if key in ('X', 'Y', 'Z') else 0):
                raise ValueError(f'Merged {key} differs')
        count += 1
    if not count:
        raise ValueError('Empty merge')
    return count


def summary(pdal, path, env):
    return json.loads(subprocess.check_output([str(pdal), 'info', '--summary', str(path)], env=env, text=True))['summary']


def equivalent_crs(wkts):
    from osgeo import osr
    refs = []
    for wkt in wkts:
        if not wkt:
            raise ValueError('Missing CRS')
        ref = osr.SpatialReference()
        if ref.ImportFromWkt(wkt) != 0:
            raise ValueError('Invalid CRS')
        refs.append(ref)
    return all(refs[0].IsSame(ref) for ref in refs[1:])


def validate(pdal, sources, merged, env):
    pdal, merged = Path(pdal), Path(merged)
    sources = [Path(s) for s in sources]
    if len(sources) < 2 or not all(p.is_file() for p in [*sources, merged]):
        raise ValueError('At least two inputs and merged output required')
    summaries = [summary(pdal, p, env) for p in [*sources, merged]]
    wkts = [s['metadata'].get('spatialreference', '') for s in summaries]
    if not equivalent_crs(wkts):
        raise ValueError('CRS differs')
    for s in summaries:
        dims = {x.strip() for x in s['dimensions'].split(',')}
        if not set(DIMENSIONS) <= dims:
            raise ValueError('Missing expected point dimensions')
    with tempfile.TemporaryDirectory(prefix='odm-merge-check-') as tmp:
        paths = []
        for idx, source in enumerate([*sources, merged]):
            output = Path(tmp)/f'{idx}.csv'; pipeline = Path(tmp)/'pipeline.json'
            pipeline.write_text(json.dumps({'pipeline': [{'type': 'readers.las', 'filename': str(source)},
                {'type': 'writers.text', 'filename': str(output), 'order': ','.join(DIMENSIONS),
                 'keep_unspecified': False, 'precision': 12}]}))
            subprocess.run([str(pdal), 'pipeline', str(pipeline)], env=env, check=True)
            paths.append(output)
        from contextlib import ExitStack
        from itertools import chain
        with ExitStack() as stack:
            readers = [csv.DictReader(stack.enter_context(p.open(newline=''))) for p in paths]
            count = compare_rows(chain.from_iterable(readers[:-1]), readers[-1])
    expected = sum(s['num_points'] for s in summaries[:-1])
    if count != expected or count != summaries[-1]['num_points']:
        raise ValueError('Summary count mismatch')
    return {'input_counts': [s['num_points'] for s in summaries[:-1]], 'merged_count': count,
            'crs_equivalent': True, 'dimensions_checked': list(DIMENSIONS),
            'coordinate_tolerance': 0.0011, 'row_order': 'concatenated inputs'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdal', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('inputs', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.pdal, args.inputs, args.output, os.environ.copy()), sort_keys=True))
