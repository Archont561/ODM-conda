"""Ephemeral research build; export only explicitly whitelisted metadata."""
import hashlib
import json
import os
import shutil
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from common import ScaffoldError, fail_cli, run, sha256
from tmp_private_odm_alt import PORT, build, replay

DATASETS = {
    'seneca': ('https://github.com/OpenDroneMap/odm_data_seneca.git', '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'),
    'copr': ('https://github.com/OpenDroneMap/odm_data_copr.git', '97cd18478ca1885f5713a11bf98d4bf96308b399'),
}

def main():
    dest = Path(os.environ['RUNNER_TEMP'])/'candidate-metadata'
    if dest.exists(): raise ScaffoldError('Metadata destination exists')
    with tempfile.TemporaryDirectory(prefix='odm-candidate-') as tmp:
        root = Path(tmp); datasets = {}
        for name, (url, commit) in DATASETS.items():
            dataset = root/name
            run(['git','init',str(dataset)])
            run(['git','-C',str(dataset),'fetch','--depth=1',url,commit])
            run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
            datasets[name] = dataset
        bundle = root/'private-bundle'
        build(bundle, PORT, datasets['seneca'])
        replay(bundle, dataset=datasets['copr'], expected_manifest_sha=sha256(bundle/'private-bundle.json'))
        inventory = json.loads((bundle/'conda-inventory.json').read_text())
        records = {p['name']: p for p in inventory['packages']}
        verified = {}
        for name in ('libspatialite','libarchive','libgdal-core','libpdal-core'):
            record = records[name]; url = record['binary_package_url']; parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != 'https' or parsed.hostname != 'conda.anaconda.org' or parsed.query or parsed.fragment:
                raise ScaffoldError('Unexpected dependency URL')
            digest=hashlib.sha256(); size=0
            with urllib.request.urlopen(url,timeout=120) as response:
                if urllib.parse.urlsplit(response.url).scheme != 'https': raise ScaffoldError('Unsafe redirect')
                while block := response.read(1024*1024):
                    size += len(block)
                    if size > 500*1024*1024: raise ScaffoldError('Archive too large')
                    digest.update(block)
            if digest.hexdigest() != record['sha256']: raise ScaffoldError('Dependency archive digest mismatch: '+name)
            verified[name] = {'url':url,'sha256':digest.hexdigest(),'bytes':size}
        private_manifest=json.loads((bundle/'private-bundle.json').read_text())
        dest.mkdir()
        for filename in ('pixi.toml','pixi.lock','conda-inventory.json','private-bundle.json'):
            shutil.copy2(bundle/filename,dest/filename)
        (dest/'verification.json').write_text(json.dumps({'scope':'Fresh research candidate; four external dependency archive bytes independently hashed; private channel archive hashes validated by bundle seal and compared with lock. Other external archive hashes are installed-record metadata only. Build/host environments separately solved and not inventoried here.', 'external_archives':verified,'private_archive_count':len([k for k in private_manifest['files'] if k.endswith('.conda')]), 'dataset_commits':{name: commit for name,(_,commit) in DATASETS.items()}},sort_keys=True,indent=2)+'\n')
        files = sorted(dest.iterdir())
        if {p.name for p in files} != {'pixi.toml','pixi.lock','conda-inventory.json','private-bundle.json','verification.json'}: raise ScaffoldError('Unexpected metadata')
        (dest/'SHA256SUMS').write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in files))
        print('::notice::CANDIDATE-METADATA '+json.dumps({'packages':len(records),'private_archives':15,'independently_hashed_external':list(verified),'lock_sha256':sha256(dest/'pixi.lock'),'manifest_sha256':sha256(dest/'private-bundle.json')},sort_keys=True,separators=(',',':')),flush=True)
    print('::notice::Both dataset replays passed; only whitelisted metadata remains for upload',flush=True)

if __name__ == '__main__': fail_cli(main)
