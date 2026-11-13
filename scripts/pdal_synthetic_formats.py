#!/usr/bin/env python3
"""Exercise PDAL LAS/LAZ, HDF and IceBridge readers using synthetic points.

Run with a separate fixture Python providing h5py/numpy; --prefix selects the
PDAL binary under test. Never use on untrusted executables. No real datasets,
accuracy certification, input-fuzzing, or release approval is implied.
"""
import argparse
import csv
import json
import os
import subprocess
import tempfile
from pathlib import Path

POINTS = [(1.25, 11.5, 101.0), (2.5, 12.25, 102.0), (3.75, 13.0, 103.0)]


def run_pipeline(pdal: Path, stages: list, directory: Path) -> None:
    pipeline = directory/'pipeline.json'
    pipeline.write_text(json.dumps({'pipeline': stages}))
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
        env.pop(key, None)
    subprocess.run([str(pdal), 'pipeline', str(pipeline)], cwd=directory, env=env, check=True)


def check_csv(path: Path) -> None:
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(POINTS): raise ValueError(f'Expected {len(POINTS)} points; got {len(rows)}')
    for row, expected in zip(rows, POINTS):
        for name, want in zip(('X', 'Y', 'Z'), expected):
            if abs(float(row[name]) - want) > 0.001:
                raise ValueError(f'Unexpected {name} value in synthetic point')


def test_formats(prefix: Path) -> dict:
    import h5py
    import numpy as np
    pdal = Path(prefix)/'bin/pdal'
    if not pdal.is_file(): raise ValueError('Missing PDAL binary in the supplied prefix')
    results = []
    with tempfile.TemporaryDirectory(prefix='pdal-formats-') as tmp:
        root = Path(tmp)
        with (root/'points.csv').open('w', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(['X','Y','Z']); writer.writerows(POINTS)
        for suffix in ('las', 'laz'):
            las = root/f'points.{suffix}'; out = root/f'{suffix}.csv'
            run_pipeline(pdal, [{'type':'readers.text','filename':str(root/'points.csv')},
                                {'type':'writers.las','filename':str(las)}], root)
            run_pipeline(pdal, [{'type':'readers.las','filename':str(las)},
                                {'type':'writers.text','filename':str(out),'order':'X,Y,Z','keep_unspecified':False}], root)
            check_csv(out); results.append(suffix)
        hdf = root/'points.h5'
        with h5py.File(hdf, 'w') as f:
            for i, name in enumerate(('x', 'y', 'z')):
                f.create_dataset(name, data=np.array([p[i] for p in POINTS], dtype=np.float32))
            for i, name in enumerate(('longitude', 'latitude', 'elevation')):
                f.create_dataset(name, data=np.array([p[i] for p in POINTS], dtype=np.float32))
            group = f.create_group('instrument_parameters')
            for name in ('time_hhmmss', 'azimuth', 'pitch', 'roll', 'gps_pdop', 'pulse_width', 'rel_time'):
                group.create_dataset(name, data=np.zeros(len(POINTS), dtype=np.float32))
            for name in ('xmt_sigstr', 'rcv_sigstr'):
                group.create_dataset(name, data=np.zeros(len(POINTS), dtype=np.int32))
        for name, reader in (
            ('hdf', {'type':'readers.hdf','filename':str(hdf),'dimensions':{'X':'/x','Y':'/y','Z':'/z'}}),
            ('icebridge', {'type':'readers.icebridge','filename':str(hdf)}),
        ):
            out=root/f'{name}.csv'
            run_pipeline(pdal,[reader,{'type':'writers.text','filename':str(out),'order':'X,Y,Z','keep_unspecified':False}],root)
            check_csv(out); results.append(name)
    return {'formats': results, 'point_count': len(POINTS),
            'scope': 'synthetic point roundtrips only; not real-data format coverage, accuracy, security, source rights or release approval'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(test_formats(args.prefix), sort_keys=True), flush=True)


if __name__ == '__main__': main()
