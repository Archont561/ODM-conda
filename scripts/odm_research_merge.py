"""Fail-closed, narrow ODM research merge for the tested LAS 1.4 format 7 schema.

Not a general replacement for lasmerge: reject unreviewed inputs and metadata.
"""
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

DIMENSIONS = frozenset(('X', 'Y', 'Z', 'Intensity', 'ReturnNumber', 'NumberOfReturns',
    'ScanDirectionFlag', 'EdgeOfFlightLine', 'Classification', 'Synthetic', 'KeyPoint',
    'Withheld', 'Overlap', 'ScanAngleRank', 'UserData', 'PointSourceId', 'GpsTime',
    'ScanChannel', 'Red', 'Green', 'Blue'))
SCALE = 0.001


def _summary(pdal, path, env):
    result = subprocess.run([str(pdal), 'info', '--summary', str(path)], check=True,
                            capture_output=True, text=True, env=env)
    return json.loads(result.stdout)['summary']


def _checked(s):
    metadata = s['metadata']
    dims = frozenset(x.strip() for x in s['dimensions'].split(','))
    if dims != DIMENSIONS or metadata['major_version'] != 1 or metadata['minor_version'] != 4 or metadata['dataformat_id'] != 7:
        raise ValueError('Unsupported LAS schema; research merge accepts only LAS 1.4 format 7 without extra dimensions')
    if not s['num_points'] or any(not math.isclose(float(metadata['scale_'+a]), SCALE, rel_tol=0, abs_tol=1e-12) for a in 'xyz'):
        raise ValueError('Empty cloud or unsupported input precision')
    bounds = s['bounds']
    for a in 'xyz':
        low, high = float(bounds['min'+a]), float(bounds['max'+a])
        if not math.isfinite(low) or not math.isfinite(high) or high < low or high-low > 4294960000*SCALE:
            raise ValueError('Invalid or unrepresentable LAS coordinate range')
    if not metadata.get('spatialreference'):
        raise ValueError('Missing spatial reference')
    return metadata['spatialreference']


def _same_crs(wkts):
    from osgeo import osr
    refs = []
    for wkt in wkts:
        ref = osr.SpatialReference()
        if ref.ImportFromWkt(wkt) != 0:
            raise ValueError('Invalid spatial reference')
        refs.append(ref)
    return all(refs[0].IsSame(ref) for ref in refs[1:])


def merge(input_files, output_file, rerun=False):
    prefix = Path(os.environ.get('ODM_CONDA_LOCAL_PREFIX', ''))
    if not prefix.is_absolute() or not prefix.is_dir():
        raise ValueError('Research merge requires an absolute Conda prefix')
    pdal = prefix/'bin/pdal'
    if not pdal.is_file() or not os.access(pdal, os.X_OK) or not pdal.resolve().is_relative_to(prefix.resolve()):
        raise ValueError('Missing prefix PDAL')
    inputs = [Path(x).resolve() for x in input_files]
    output = Path(output_file)
    if len(inputs) < 2 or len(set(inputs)) != len(inputs) or not all(p.is_file() for p in inputs):
        raise ValueError('Research merge requires at least two distinct input files')
    if output.suffix.lower() != '.laz' or output.resolve() in inputs or not output.parent.is_dir() or output.is_symlink():
        raise ValueError('Unsafe research merge output')
    if output.exists() and not rerun:
        raise ValueError('Research merge output already exists')
    env = os.environ.copy()
    env['PROJ_LIB'] = env['PROJ_DATA'] = str(prefix/'share/proj')
    summaries = [_summary(pdal, p, env) for p in inputs]
    wkts = [_checked(s) for s in summaries]
    if not _same_crs(wkts):
        raise ValueError('Input CRS differs')
    # Validate the combined span too, not just each individual cloud.
    for a in 'xyz':
        low = min(s['bounds']['min'+a] for s in summaries)
        high = max(s['bounds']['max'+a] for s in summaries)
        if high-low > 4294960000*SCALE:
            raise ValueError('Combined coordinate range is not representable')
    fd, name = tempfile.mkstemp(prefix='.odm-merge-', suffix='.laz', dir=output.parent)
    os.close(fd); tmp = Path(name)
    try:
        cmd = [str(pdal), 'merge', *map(str, inputs), str(tmp),
               *[f'--writers.las.scale_{a}={SCALE}' for a in 'xyz'],
               *[f'--writers.las.offset_{a}=auto' for a in 'xyz'],
               '--writers.las.minor_version=4', '--writers.las.dataformat_id=7']
        subprocess.run(cmd, env=env, check=True)
        if not tmp.is_file() or tmp.stat().st_size == 0:
            raise ValueError('PDAL did not produce a nonempty merge')
        result = _summary(pdal, tmp, env)
        if result['num_points'] != sum(s['num_points'] for s in summaries):
            raise ValueError('Merged point count mismatch')
        if not _same_crs([*wkts, _checked(result)]):
            raise ValueError('Output CRS differs')
        for a in 'xyz':
            for side, op in (('min', min), ('max', max)):
                expected = op(s['bounds'][side+a] for s in summaries)
                if abs(result['bounds'][side+a] - expected) > SCALE*1.1:
                    raise ValueError('Merged bounds differ')
        os.replace(tmp, output)
    finally:
        tmp.unlink(missing_ok=True)
