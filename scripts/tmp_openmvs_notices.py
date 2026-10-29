"""Temporary local-only build input review; never upload binaries or archives."""
import json
import hashlib
import re
from collections import Counter
import difflib
import tarfile
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.cwd()

def run(*args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run([str(x) for x in args], check=True)

with tempfile.TemporaryDirectory(prefix='openmvs-review-', dir=os.environ['RUNNER_TEMP']) as tmp:
    root = Path(tmp)
    run('python', ROOT/'scripts/check_open_research_sources.py', 'openmvs', '--cache', root/'sources')
    out = root/'output'
    run('rattler-build','build','--recipe', ROOT/'research/recipes/openmvs-odm/recipe.yaml',
        '--target-platform','linux-64','--variant-config', ROOT/'recipes/variants.yaml',
        '--channel','conda-forge','--channel-priority','strict','--output-dir',out,'--log-style','plain','--keep-build')
    prefixes = list(out.glob('bld/*/host_env*/conda-meta'))
    assert len(prefixes) == 1, prefixes
    records = [json.loads(p.read_text()) for p in prefixes[0].glob('*.json')]
    names = {'cgal-cpp', 'libboost', 'libboost-devel', 'boost-cpp', 'eigen', 'eigen-abi', 'mpfr', 'gmp', 'libopencv', 'tbb', 'tbb-devel'}
    hits = [x for x in records if x.get('name') in names]
    assert any(x.get('name') == 'cgal-cpp' for x in hits), [x.get('name') for x in records]
    compact = [{k:x.get(k) for k in ('name','version','build','sha256','license','fn')} for x in sorted(hits, key=lambda a:a['name'])]
    print('::notice::Native host metadata ' + json.dumps(compact, separators=(',',':')), flush=True)
    builds = list(out.glob('bld/*/reduced-openmvs-*/first/.research-build'))
    assert len(builds) == 1, builds
    dep = subprocess.check_output(['ninja','-C',str(builds[0]),'-t','deps'],text=True)
    host = str(prefixes[0].parent) + '/include/'
    for library in ('CGAL/','boost/'):
        paths = sorted({line.strip().split(host,1)[1] for line in dep.splitlines() if host in line and (host+library) in line})
        print(f'::notice::{library} native dependency trace count={len(paths)} sample=' + ','.join(paths[:15]),flush=True)
        headers = [prefixes[0].parent/'include'/p for p in paths]
        labels = Counter()
        for header in headers:
            text = header.read_text(errors='replace')[:10000]
            spdx = re.search(r'SPDX-License-Identifier:\s*([^\r\n*]+)', text)
            label = spdx.group(1).strip() if spdx else ('BSL-reference' if 'Boost Software License' in text else 'no-SPDX-or-Boost-reference-in-first-10k')
            labels[label] += 1
        print(f'::notice::{library} header marker counts ' + json.dumps(labels,sort_keys=True),flush=True)
        if library == 'CGAL/':
            for item in ('CGAL/AABB_tree.h','CGAL/AABB_traits_3.h'):
                file = prefixes[0].parent/'include'/item
                print(f'::notice::installed {item} SHA256={hashlib.sha256(file.read_bytes()).hexdigest()}',flush=True)
    # Compare actual installed package headers with public upstream tag, inside scratch only.
    archive = root/'cgal-tag.tar.gz'
    run('curl', '-fsSL', 'https://codeload.github.com/CGAL/cgal/tar.gz/refs/tags/v6.2.1', '-o', archive)
    print('::notice::CGAL v6.2.1 tag archive SHA256=' + hashlib.sha256(archive.read_bytes()).hexdigest(), flush=True)
    upstream = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if not member.isfile() or '/include/CGAL/' not in member.name:
                continue
            key = 'CGAL/' + member.name.split('/include/CGAL/',1)[1]
            if key in upstream:
                upstream[key] = None
            else:
                upstream[key] = tar.extractfile(member).read()
    hostdir = prefixes[0].parent/'include'
    traced_cgal = sorted({line.strip().split(host,1)[1] for line in dep.splitlines() if host+'CGAL/' in line})
    categories = Counter()
    gpl_paths = []
    for rel in traced_cgal:
        data=(hostdir/rel).read_bytes()
        text=data[:10000].decode(errors='replace')
        marker = re.search(r'SPDX-License-Identifier:\s*([^\r\n*]+)',text)
        if marker and marker.group(1).strip() == 'GPL-3.0-or-later OR LicenseRef-Commercial':
            gpl_paths.append(rel)
        public = upstream.get(rel)
        categories['missing_or_ambiguous' if public is None else ('identical' if public == data else 'different')] += 1
    print('::notice::CGAL traced tag comparison ' + json.dumps(categories,sort_keys=True),flush=True)
    for start in range(0,len(gpl_paths),30):
        print('::notice::CGAL GPL-or-commercial traced paths ' + json.dumps(gpl_paths[start:start+30],separators=(',',':')),flush=True)
    for rel in ('CGAL/AABB_tree.h','CGAL/AABB_traits_3.h'):
        actual=(hostdir/rel).read_text().splitlines()
        original=upstream[rel].decode().splitlines()
        diff=list(difflib.unified_diff(original,actual,fromfile='upstream',tofile='installed',lineterm=''))
        print('::notice::CGAL sample diff ' + rel + ' diff_lines=' + str(len(diff)) + ' first=' + json.dumps(diff[:16],separators=(',',':')),flush=True)
    boostpaths = sorted({line.strip().split(host,1)[1] for line in dep.splitlines() if host+'boost/' in line})
    unresolved=[]
    for rel in boostpaths:
        text=(hostdir/rel).read_text(errors='replace')[:10000]
        if 'Boost Software License' not in text and not re.search(r'SPDX-License-Identifier:',text):
            unresolved.append(rel)
    print('::notice::Boost no-marker paths count=' + str(len(unresolved)) + ' sample=' + json.dumps(unresolved[:30],separators=(',',':')),flush=True)
    dep_lines = {line.strip() for line in dep.splitlines() if '/Eigen/' in line}
    host_eigen = {line for line in dep_lines if line.startswith(host)}
    vendored_eigen = {line for line in dep_lines if '/_external/eigen/' in line}
    print(f'::notice::Eigen path counts host={len(host_eigen)} vendored={len(vendored_eigen)} total={len(dep_lines)}',flush=True)
    matches=list((out/'linux-64').glob('openmvs-odm-*.conda'))
    assert len(matches)==1, matches
    run('rattler-build','test','--package-file',matches[0],'--channel','conda-forge','--channel-priority','strict','--output-dir',root/'retest','--log-style','plain')
    run('python', ROOT/'scripts/audit_open_research.py', 'openmvs-odm', matches[0])
    print('::notice::Reduced-tree host-inspection build, fresh retest and audit passed; all inputs discarded', flush=True)
