#!/usr/bin/env python3
"""Check exact RenderDEM artifact and source bytes, without uploading them."""
import hashlib
import io
import json
import os
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from common import first_comment, sha256
from package_archive import read_package

COMMIT='8c0619224de35ceef02a4f5863b182a9a4574947'
SOURCE_SHA='748cb2839db7d24ee3fdce034e8637829630a9d68ec6561fb76523e25d24af8d'


def main():
    zip_path=Path(os.environ['RUNNER_TEMP'])/'original.zip'
    assert sha256(zip_path)=='cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
    with tempfile.TemporaryDirectory(prefix='renderdem-review-') as directory:
        with zipfile.ZipFile(zip_path) as archive:
            files=[n for n in archive.namelist() if not n.endswith('/')]
            assert len(files)==3 and len(files)==len(set(files))
            packages=[n for n in files if n.endswith('.conda')]
            bundles=[n for n in files if n.endswith('.tar.gz')]
            assert len(packages)==len(bundles)==1
            package=Path(directory)/'renderdem-1.0-h873e7db_1.conda'
            package.write_bytes(archive.read(packages[0]))
            source_bytes=archive.read(bundles[0])
        assert sha256(package)=='a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'
        assert hashlib.sha256(source_bytes).hexdigest()=='bf806435fc489b73c059e409b85c159e2b01f3bac7537f996e39d842bd6f8ec1'
        info,payload=read_package(package)
        with tarfile.open(fileobj=io.BytesIO(source_bytes),mode='r:gz') as bundle:
            names=bundle.getnames()
            assert len(names)==len(set(names))
            manifest=json.load(bundle.extractfile('SOURCE-MANIFEST.json'))
            assert manifest['packaging_commit']==COMMIT and manifest['packaging_dirty'] is False
            packaging=0
            for path,digest in manifest['files'].items():
                data=bundle.extractfile(path).read()
                assert hashlib.sha256(data).hexdigest()==digest
                if path.startswith('packaging/'):
                    relative=path.removeprefix('packaging/')
                    assert '..' not in PurePosixPath(relative).parts
                    tracked=subprocess.check_output(['git','show',f'{COMMIT}:{relative}'])
                    assert data==tracked, relative
                    packaging+=1
            upstream=[n for n in names if n.startswith('upstream/') and n.endswith('.tar.gz')]
            assert len(upstream)==1
            upstream_bytes=bundle.extractfile(upstream[0]).read()
            assert hashlib.sha256(upstream_bytes).hexdigest()==SOURCE_SHA
        with tarfile.open(fileobj=io.BytesIO(upstream_bytes),mode='r:gz') as upstream:
            regular=[m for m in upstream.getmembers() if m.isfile()]
            assert len(regular)==11
            def read(suffix):
                matches=[m for m in regular if m.name.split('/',1)[1]==suffix]
                assert len(matches)==1
                return upstream.extractfile(matches[0]).read()
            notices={'renderdem-AGPL-3.0.txt':read('LICENSE'), 'cxxopts-MIT.txt':first_comment(read('vendor/cxxopts.hpp')),
                     'packaging-MIT.txt':subprocess.check_output(['git','show',f'{COMMIT}:LICENSE'])}
        evidence={}
        for target,expected in notices.items():
            installed=payload['share/licenses/renderdem/'+target]
            metadata=[value for path,value in info.items() if path.startswith('info/licenses/') and PurePosixPath(path).name==target]
            assert installed==expected and len(metadata)==1 and metadata[0]==expected, target
            evidence[target]=hashlib.sha256(expected).hexdigest()
        result={'packaging_entries_compared_to_git':packaging,'source_manifest_files':len(manifest['files']),
                'upstream_regular_files':len(regular),'notices_sha256':evidence,'package_sha256':sha256(package),
                'source_sha256':hashlib.sha256(source_bytes).hexdigest()}
        print('::notice::RESULT '+json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)

if __name__=='__main__': main()
