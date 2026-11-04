#!/usr/bin/env python3
"""Temporary read-only inspection of an owner-dispatched build artifact."""
import hashlib
import json
import os
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from audit_package import audit
from common import ROOT, config, rattler, run, sha256, source_bundle_name
from package_archive import read_package


def main():
    name='renderdem'; component=config()['components'][name]
    archive=Path(os.environ['RUNNER_TEMP'])/'input.zip'
    assert sha256(archive)=='cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
    with tempfile.TemporaryDirectory(prefix='odm-artifact-inspect-') as temporary:
        work=Path(temporary)
        with zipfile.ZipFile(archive) as zipped:
            files=[]
            for item in zipped.infolist():
                path=PurePosixPath(item.filename)
                if item.is_dir(): continue
                if path.is_absolute() or '..' in path.parts or '\\' in item.filename or stat.S_ISLNK(item.external_attr >> 16): raise ValueError('Unsafe ZIP path')
                files.append(item)
            if len(files)!=3 or len({x.filename for x in files})!=3: raise ValueError('Expected exactly three artifact files')
            for item in files:
                target=work/Path(item.filename); target.parent.mkdir(parents=True,exist_ok=True)
                with zipped.open(item) as source, target.open('xb') as destination:
                    while block:=source.read(1024*1024): destination.write(block)
        packages=list(work.rglob('*.conda')); bundles=list(work.rglob('source-*.tar.gz')); reports=list(work.rglob('audit-*.json'))
        if len(packages)!=1 or len(bundles)!=1 or len(reports)!=1 or bundles[0].name!=source_bundle_name(name,component) or reports[0].name!='audit-renderdem.json': raise ValueError('Artifact selection is not exclusively renderdem')
        package=packages[0]; bundle=bundles[0]
        report=audit(name,component,package)
        info,payload=read_package(package); index=json.loads(info['info/index.json'])
        existing=json.loads(reports[0].read_text())
        with tarfile.open(bundle,'r:gz') as source:
            manifest=json.load(source.extractfile('SOURCE-MANIFEST.json'))
            if (manifest['component'],manifest['version'],manifest['build_number'],manifest['packaging_commit'],manifest['packaging_dirty']) != (name,component['version'],component['build_number'],'8c0619224de35ceef02a4f5863b182a9a4574947',False): raise ValueError('Unexpected source manifest identity')
            if len(source.getnames())!=len(set(source.getnames())): raise ValueError('Duplicate source archive members')
            for path, expected in manifest['files'].items():
                member=source.getmember(path)
                if not member.isfile(): raise ValueError('Unexpected non-file manifest member')
                actual=hashlib.sha256(source.extractfile(member).read()).hexdigest()
                if actual!=expected: raise ValueError(f'Source hash mismatch: {path}')
        run([rattler(),'test','--package-file',str(package),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(work/'fresh-test'),'--log-style','plain'])
        result={'component':name,'package':package.name,'package_sha256':sha256(package),'source':bundle.name,'source_sha256':sha256(bundle),'packaging_commit':manifest['packaging_commit'],'listed_source_files':len(manifest['files']),'artifact_zip_sha256':sha256(archive),'runtime_dependencies':index.get('depends',[]),'license':component['license'],'report_present':bool(existing),'reaudit':bool(report)}
        print('::notice::RESULT '+json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)
        print('::notice::Artifact identity, source manifest hashes, package re-audit and fresh test passed; no artifact upload and no release approval.',flush=True)

if __name__=='__main__': main()
