import base64
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from inventory_conda_environment import inventory
from private_conda_channel import create

root = Path(os.environ['RUNNER_TEMP'])
package_name = 'renderdem-1.0-h873e7db_1.conda'
expected = 'a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'
def sha(b): return hashlib.sha256(b).hexdigest()

if sys.argv[1] == 'prepare':
    path = root/'original.zip'
    assert sha(path.read_bytes()) == 'cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith('/'+package_name) or n == package_name]
        assert len(names) == 1 and len(set(archive.namelist())) == len(archive.namelist())
        data = archive.read(names[0])
    assert sha(data) == expected
    package = root/package_name; package.write_bytes(data)
    create([package], root/'channel')
    project = root/'runtime'; project.mkdir()
    (project/'pixi.toml').write_text('[workspace]\nname = "renderdem-link-review"\nversion = "0.1.0"\nchannels = ["'+(root/'channel').as_uri()+'", "conda-forge"]\nplatforms = ["linux-64"]\n\n[dependencies]\nrenderdem = "==1.0"\n')
elif sys.argv[1] == 'inspect':
    prefix = root/'runtime/.pixi/envs/default'
    actual = inventory(prefix)['packages']
    reference = json.loads(Path('research/renderdem-runtime-closure-2026-11-06.json').read_text())['runtime_inventory']['packages']
    identity = lambda a: {(r['name'],r['version'],r['build'],r['sha256']) for r in a}
    assert identity(actual) == identity(reference) and len(actual) == len(reference) == 66
    patterns = {'renderdem':'bin/renderdem','pdal':'lib/libpdalcpp.so.*','gdal':'lib/libgdal.so.*','archive':'lib/libarchive.so.*','spatialite':'lib/libspatialite.so.*','rttopo':'lib/librttopo.so.*','lzo':'lib/liblzo2.so.*','readline':'lib/libreadline.so.*','geos':'lib/libgeos_c.so.*','gomp':'lib/libgomp.so.*'}
    objects = {}
    for label, pattern in patterns.items():
        candidates = [p for p in prefix.glob(pattern) if p.is_file()]
        real = {p.resolve() for p in candidates}
        assert len(real) == 1, (label, candidates)
        path = real.pop()
        assert path.is_relative_to(prefix.resolve())
        dynamic = subprocess.check_output(['readelf','-d',str(path)], text=True)
        objects[label] = {'path': path.relative_to(prefix.resolve()).as_posix(), 'sha256':sha(path.read_bytes()), 'needed': re.findall(r'\(NEEDED\).*?\[([^\]]+)\]',dynamic), 'soname':re.findall(r'\(SONAME\).*?\[([^\]]+)\]',dynamic), 'rpath':re.findall(r'\((?:RPATH|RUNPATH)\).*?\[([^\]]+)\]',dynamic)}
    raw=json.dumps({'candidate_sha256':expected,'runtime_identity_match':True,'objects':objects,'scope':'readelf dynamic sections for selected files in one fresh runtime prefix; no general runtime loading, static link, plugins, legal or final-release conclusion'},sort_keys=True,indent=2).encode()
    encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode(); chunks=[encoded[i:i+2700] for i in range(0,len(encoded),2700)]; assert len(chunks)<=30
    print(f'::notice::LINK-INFO chunks={len(chunks)} sha256={sha(raw)}',flush=True)
    for i,chunk in enumerate(chunks): print(f'::notice::LINK-CHUNK-{i:02d} {chunk}',flush=True)
else: raise ValueError('Unknown operation')
