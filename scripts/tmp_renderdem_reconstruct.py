#!/usr/bin/env python3
"""Test build using the retained RenderDEM source bundle without publishing it."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from common import rattler, run, sha256
from source_graph import unpack_archive

ZIP_SHA='cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
BUNDLE_SHA='bf806435fc489b73c059e409b85c159e2b01f3bac7537f996e39d842bd6f8ec1'
SOURCE_SHA='748cb2839db7d24ee3fdce034e8637829630a9d68ec6561fb76523e25d24af8d'


def main():
    zipped=Path(os.environ['RUNNER_TEMP'])/'original.zip'
    assert sha256(zipped)==ZIP_SHA
    with tempfile.TemporaryDirectory(prefix='renderdem-source-rebuild-') as tmp:
        root=Path(tmp); packaging=root/'packaging'; packaging.mkdir()
        with zipfile.ZipFile(zipped) as z:
            names=[n for n in z.namelist() if n.endswith('source-renderdem-1.0-b1.tar.gz')]
            assert len(names)==1
            bundle=z.read(names[0]); assert hashlib.sha256(bundle).hexdigest()==BUNDLE_SHA
        with tarfile.open(fileobj=io.BytesIO(bundle),mode='r:gz') as t:
            assert len(t.getnames())==len(set(t.getnames()))
            manifest=json.load(t.extractfile('SOURCE-MANIFEST.json'))
            assert (manifest['component'],manifest['build_number'],manifest['packaging_commit'])==('renderdem',1,'8c0619224de35ceef02a4f5863b182a9a4574947')
            for name,digest in manifest['files'].items():
                path=PurePosixPath(name)
                assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
                member=t.getmember(name); assert member.isfile()
                data=t.extractfile(member).read(); assert hashlib.sha256(data).hexdigest()==digest
                if name.startswith('packaging/'):
                    target=packaging.joinpath(*path.parts[1:]); target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(data); target.chmod(0o755 if member.mode & 0o111 else 0o644)
                elif name.startswith('upstream/'):
                    assert hashlib.sha256(data).hexdigest()==SOURCE_SHA
                    (root/'upstream.tar.gz').write_bytes(data)
                else: raise ValueError('Unexpected source bundle entry')
        source=root/'unpacked-source'; source.mkdir();unpack_archive(root/'upstream.tar.gz',source)
        recipe=packaging/'recipes/renderdem/recipe.yaml'; text=recipe.read_text()
        old='  url: https://codeload.github.com/OpenDroneMap/RenderDEM/tar.gz/93502f2e225be0cebcb8663db3bc5058baa3eb1e\n  sha256: ${{ source_sha256 }}\n'
        assert text.count(old)==1
        recipe.write_text(text.replace(old,'  path: '+json.dumps(str(source))+'\n'))
        output=root/'output'
        run([rattler(),'build','--recipe',str(recipe),'--target-platform','linux-64','--variant-config',str(packaging/'recipes/variants.yaml'),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(output),'--log-style','plain'])
        packages=list((output/'linux-64').glob('renderdem-1.0-*.conda')); assert len(packages)==1
        run([rattler(),'test','--package-file',str(packages[0]),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(root/'retest'),'--log-style','plain'])
        run([sys.executable,str(packaging/'scripts/audit_package.py'),'--component','renderdem','--output-dir',str(output),'--reports-dir',str(root/'reports')])
        report=json.loads((root/'reports/audit-renderdem.json').read_text())
        print('::notice::RESULT '+json.dumps({'source_bundle_sha256':BUNDLE_SHA,'upstream_sha256':SOURCE_SHA,'packaging_files':len(manifest['files'])-1,'rebuilt_package':packages[0].name,'rebuilt_sha256':sha256(packages[0]),'original_sha256':'a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c','needed':report['elf_needed'],'rpath':report['rpath']},sort_keys=True,separators=(',',':')),flush=True)


if __name__=='__main__': main()
