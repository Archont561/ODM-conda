#!/usr/bin/env python3
"""Capture a bounded fresh runtime solve of the verified RenderDEM package."""
import json
import os
import tempfile
import zipfile
from pathlib import Path
from common import run, sha256
from inventory_conda_environment import inventory
from private_conda_channel import create
from private_odm_bundle import loopback


def main():
    archive=Path(os.environ['RUNNER_TEMP'])/'original.zip'
    with tempfile.TemporaryDirectory(prefix='renderdem-solve-') as temporary:
        root=Path(temporary)
        with zipfile.ZipFile(archive) as zipped:
            files=[n for n in zipped.namelist() if n.endswith('.conda')]
            assert len(files)==1
            package=root/'renderdem-1.0-h873e7db_1.conda';package.write_bytes(zipped.read(files[0]))
        assert sha256(package)=='a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'
        create([package],root/'channel')
        project=root/'project'; env=os.environ.copy(); env['HOME']=str(root/'home'); env['XDG_CACHE_HOME']=str(root/'cache'); env['RATTLER_CACHE_DIR']=str(root/'cache/rattler'); (root/'home').mkdir()
        with loopback(root/'channel',48179) as channel:
            run(['pixi','init','--format','pixi','--scm','github','--channel',channel,'--channel','conda-forge','--platform','linux-64',str(project)],env=env)
            run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'renderdem'],env=env)
        entries=inventory(project/'.pixi/envs/default')['packages']
        selected=[{k:p[k] for k in ('name','version','build','sha256','license')} for p in entries if p['name'] in ('renderdem','libpdal-core','libgdal-core','libgomp','libgcc','libstdcxx')]
        assert len(selected)==6
        print('::notice::FRESH_SOLVE '+json.dumps({'count':len(entries),'selected':selected},sort_keys=True,separators=(',',':')),flush=True)

if __name__=='__main__':main()
