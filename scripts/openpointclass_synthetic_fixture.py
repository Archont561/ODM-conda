#!/usr/bin/env python3
"""Exercise a trusted OpenPointClass model on generated LAZ; not accuracy proof."""
import argparse
import csv
import json
import math
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


def pipeline(pdal: Path, stages: list, directory: Path, env: dict):
    path = directory/'pipeline.json'
    path.write_text(json.dumps({'pipeline': stages}))
    subprocess.run([str(pdal), 'pipeline', str(path)], env=env, cwd=directory, check=True)


def check_output(path: Path, expected_count: int) -> dict:
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != expected_count:
        raise ValueError('Classifier changed point count')
    classes = Counter()
    for row in rows:
        if not all(math.isfinite(float(row[k])) for k in ('X', 'Y', 'Z')):
            raise ValueError('Nonfinite output coordinates')
        value = int(float(row['Classification']))
        if not 0 <= value <= 255:
            raise ValueError('Invalid output classification')
        classes[value] += 1
    if all(code == 1 for code in classes):
        raise ValueError('No points classified beyond unclassified')
    return {'point_count': len(rows), 'classification_counts': dict(sorted(classes.items()))}


def run_fixture(prefix: Path, model: Path) -> dict:
    pdal, classifier = prefix/'bin/pdal', prefix/'bin/pcclassify'
    if not pdal.is_file() or not classifier.is_file() or not model.is_file():
        raise ValueError('Missing tested binaries or model')
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
        env.pop(key, None)
    env['PROJ_DATA'] = env['PROJ_LIB'] = str(prefix/'share/proj')
    env['PATH'] = str(prefix/'bin') + os.pathsep + os.defpath
    env['OMP_NUM_THREADS'] = '2'
    with tempfile.TemporaryDirectory(prefix='opc-synthetic-') as tmp:
        root = Path(tmp); source = root/'points.csv'; count = 2500
        with source.open('w', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(['X', 'Y', 'Z', 'Red', 'Green', 'Blue', 'Classification'])
            for i in range(50):
                for j in range(50):
                    writer.writerow([i*0.2, j*0.2, 0.3*math.sin(i/5)+0.2*math.cos(j/6), 30000, 20000, 10000, 1])
        inp, out, csv_out = root/'input.laz', root/'classified.laz', root/'output.csv'
        pipeline(pdal, [{'type': 'readers.text', 'filename': str(source)}, {'type': 'writers.las', 'filename': str(inp)}], root, env)
        subprocess.run([str(classifier), str(inp), str(out), str(model), '-u', '-s', '2,64'], cwd=root, env=env, check=True, timeout=300)
        pipeline(pdal, [{'type': 'readers.las', 'filename': str(out)}, {'type': 'writers.text', 'filename': str(csv_out), 'order': 'X,Y,Z,Classification', 'keep_unspecified': False}], root, env)
        return check_output(csv_out, count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run_fixture(args.prefix.resolve(), args.model.resolve()), sort_keys=True))


if __name__ == '__main__':
    main()
