"""Temporary local-only build input review; never upload binaries or archives."""
import json
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
    matches=list((out/'linux-64').glob('openmvs-odm-*.conda'))
    assert len(matches)==1, matches
    run('rattler-build','test','--package-file',matches[0],'--channel','conda-forge','--channel-priority','strict','--output-dir',root/'retest','--log-style','plain')
    run('python', ROOT/'scripts/audit_open_research.py', 'openmvs-odm', matches[0])
    print('::notice::Reduced-tree host-inspection build, fresh retest and audit passed; all inputs discarded', flush=True)
