#!/usr/bin/env python3
"""Summarize ephemeral test artifacts without uploading packages or sources."""
import hashlib
import json
import os
import tarfile
from pathlib import Path
from common import ROOT, config, find_package, sha256, source_bundle_name

name=os.environ['COMPONENT']
component=config()['components'][name]
package=find_package(name, component, ROOT/'output')
source=ROOT/'source-bundles'/source_bundle_name(name,component)
with tarfile.open(source,'r:gz') as archive:
    manifest=json.load(archive.extractfile('SOURCE-MANIFEST.json'))
    assert manifest['component']==name and manifest['version']==component['version']
    for path, expected in manifest['files'].items():
        assert hashlib.sha256(archive.extractfile(path).read()).hexdigest()==expected, path
print(f'::notice::{name} package {package.name} sha256 {sha256(package)}; source sha256 {sha256(source)}; verified {len(manifest["files"])} listed source files; packaging commit {manifest["packaging_commit"]}; dirty {manifest["packaging_dirty"]}',flush=True)
