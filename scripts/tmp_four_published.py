"""Temporary read-only integration check; no component or dataset uploads."""
import json
import os
import subprocess
import tempfile
from pathlib import Path


def run(*args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run([str(x) for x in args], check=True)


def main():
    with tempfile.TemporaryDirectory(prefix='published-integration-', dir=os.environ['RUNNER_TEMP']) as temp:
        project = Path(temp)
        manifest = project / 'pixi.toml'
        manifest.write_text('''[workspace]
name = "published-components-test"
channels = ["https://prefix.dev/archont561/archont561", "conda-forge"]
platforms = ["linux-64"]

[dependencies]
python = ">=3.12,<3.13"
py-opencv = ">=4.12,<4.13"
pdal = "*"
python-pdal = "*"
gdal = "*"
exiftool = "*"
fastrasterfilter = { version = "==1.0", build = "h873e7db_2" }
fpcfilter = { version = "==0.2", build = "h873e7db_1" }
dem2points = { version = "==0.0.0.dev20220721", build = "h873e7db_2" }
odm-orthophoto = { version = "==0.0.0.dev20250225", build = "h873e7db_2" }
''')
        run('pixi', 'install', '--manifest-path', manifest)
        output = subprocess.check_output(['pixi', 'list', '--manifest-path', str(manifest), '--locked', '--json'], text=True)
        records = json.loads(output)
        expected = {
            'fpcfilter': '8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679',
            'fastrasterfilter': '2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4',
            'dem2points': 'd7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f',
            'odm-orthophoto': 'c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614',
        }
        selected = {item['name']: item for item in records}
        for name, digest in expected.items():
            item = selected[name]
            assert item['sha256'] == digest, (name, item['sha256'], digest)
            print(f"::notice::Verified {item['file_name']} SHA256 {digest}", flush=True)
        print(f'::notice::Combined solve has {len(records)} packages; all component hashes match published records', flush=True)
        for group in [records[i:i + 30] for i in range(0, len(records), 30)]:
            line = '; '.join(f"{x['file_name']} SHA256={x.get('sha256') or 'missing'}" for x in group)
            print(f'::notice::SOLVE {line}', flush=True)
        prefix = project / '.pixi/envs/default'
        for component in ('fpcfilter', 'dem2points', 'fastrasterfilter', 'odm-orthophoto'):
            fixture = prefix / 'share' / 'odm-conda' / component / 'functional_test.py'
            run('pixi', 'run', '--manifest-path', manifest, '--locked', 'python', fixture)
            print(f'::notice::PASS combined prefix installed fixture and linkage: {component}', flush=True)
        run('pixi', 'run', '--manifest-path', manifest, '--locked', 'python', '-c',
            'import cv2, pdal; from osgeo import gdal; print("IMPORTS", cv2.__version__, gdal.VersionInfo(), pdal.__version__)')
        print('::notice::PASS combined prefix OpenCV, GDAL and PDAL Python imports', flush=True)

if __name__ == '__main__':
    main()
