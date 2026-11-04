#!/usr/bin/env python3
"""Test the exact owner-dispatched artifact in fresh, relocated installations."""
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from common import run, sha256
from inventory_conda_environment import inventory
from private_conda_channel import create
from private_odm_bundle import inventory_identities, loopback
from validate_renderdem_laz import validate


def main():
    zip_path=Path(os.environ['RUNNER_TEMP'])/'original.zip'
    assert sha256(zip_path)=='cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
    output=Path(os.environ['RUNNER_TEMP'])/'review-metadata'; output.mkdir(mode=0o700)
    with tempfile.TemporaryDirectory(prefix='renderdem-replay-') as temporary:
        root=Path(temporary)
        with zipfile.ZipFile(zip_path) as archive:
            matches=[n for n in archive.namelist() if n.endswith('.conda')]
            assert len(matches)==1
            package=root/'renderdem-1.0-h873e7db_1.conda';package.write_bytes(archive.read(matches[0]))
        assert sha256(package)=='a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'
        create([package],root/'channel')
        with loopback(root/'channel',48179) as channel:
            first=root/'first/project'; first.parent.mkdir()
            env=os.environ.copy(); env['HOME']=str(root/'home1'); env['XDG_CACHE_HOME']=str(root/'cache1'); env['RATTLER_CACHE_DIR']=str(root/'cache1/rattler'); (root/'home1').mkdir()
            run(['pixi','init','--format','pixi','--scm','github','--channel',channel,'--channel','conda-forge','--platform','linux-64',str(first)],env=env)
            run(['pixi','add','--manifest-path',str(first/'pixi.toml'),'renderdem','pdal==2.10.0'],env=env)
            inv=inventory(first/'.pixi/envs/default'); identities=inventory_identities(inv)
            assert any(p['name']=='renderdem' and p['sha256']==sha256(package) for p in inv['packages'])
            validate(first/'.pixi/envs/default')
            second=root/'relocated/project'; second.mkdir(parents=True)
            for name in ('pixi.toml','pixi.lock'): shutil.copy2(first/name,second/name)
            fresh=env.copy();fresh['HOME']=str(root/'home2');fresh['XDG_CACHE_HOME']=str(root/'cache2');fresh['RATTLER_CACHE_DIR']=str(root/'cache2/rattler');(root/'home2').mkdir()
            run(['pixi','install','--manifest-path',str(second/'pixi.toml'),'--locked'],env=fresh)
            assert (first/'pixi.lock').read_bytes()==(second/'pixi.lock').read_bytes()
            assert inventory_identities(inventory(second/'.pixi/envs/default'))==identities
            validate(second/'.pixi/envs/default')
            for name in ('pixi.toml','pixi.lock'): shutil.copy2(first/name,output/name)
            (output/'conda-inventory.json').write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n')
            (output/'README.txt').write_text('Research metadata only; no binaries, source archives or data. Includes separate PDAL CLI for LAZ test. Loopback package URL refers to a discarded local channel; this metadata alone cannot replay the package. Not a release lock, source offer or approval.\n')
            files=('pixi.toml','pixi.lock','conda-inventory.json','README.txt')
            (output/'SHA256SUMS').write_text(''.join(f'{sha256(output/name)}  {name}\n' for name in files))
            print(f'::notice::RESULT {len(identities)} matching Conda records; lock SHA256 {sha256(output/"pixi.lock")}; package SHA256 {sha256(package)}; PLY/LAS/LAZ and relocated locked install passed',flush=True)


if __name__=='__main__': main()
