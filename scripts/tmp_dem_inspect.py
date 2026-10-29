import hashlib, io, json, subprocess, sys, tarfile, tempfile, traceback, zipfile
from pathlib import Path, PurePosixPath
from common import config, first_comment
from audit_package import audit
from package_archive import read_package

sys.excepthook = lambda typ, value, tb: print('::error::' + ' '.join(traceback.format_exception(typ, value, tb)).replace('\n', ' '))
def sha(data): return hashlib.sha256(data).hexdigest()
def notice(message): print('::notice::' + message, flush=True)

zip_path = Path('/tmp/dem-validation.zip')
assert sha(zip_path.read_bytes()) == '432b5b58d45d0cc3844a9980afc1ba84b0fb8f92da75af3b93d1863d33236d5f'
with tempfile.TemporaryDirectory() as temp, zipfile.ZipFile(zip_path) as z:
    members = z.namelist()
    notice('Artifact members: ' + json.dumps(members))
    packages = [n for n in members if n.endswith('.conda')]
    bundles = [n for n in members if n.endswith('.tar.gz')]
    assert len(packages) == len(bundles) == 1 and Path(packages[0]).name.startswith('dem2mesh-') and Path(bundles[0]).name.startswith('source-dem2mesh-'), 'Artifact is not dem2mesh-only'
    package = Path(temp) / Path(packages[0]).name
    package.write_bytes(z.read(packages[0]))
    component = config()['components']['dem2mesh']
    result = audit('dem2mesh', component, package)
    info, payload = read_package(package)
    bundle = z.read(bundles[0])
    notice('Source bundle SHA256: ' + sha(bundle))
    with tarfile.open(fileobj=io.BytesIO(bundle), mode='r:gz') as src:
        manifest = json.load(src.extractfile('SOURCE-MANIFEST.json'))
        assert manifest['packaging_commit'] == '87a6098968fb25be4ca7e972b86c3dcf73ffbe70' and manifest['packaging_dirty'] is False
        for path, digest in manifest['files'].items():
            assert sha(src.extractfile(path).read()) == digest, path
        archives = [n for n in manifest['files'] if n.startswith('upstream/dem2mesh-') and n.endswith('.tar.gz')]
        assert len(archives) == 1
        upstream = src.extractfile(archives[0]).read()
        assert sha(upstream) == component['source']['sha256']
        with tarfile.open(fileobj=io.BytesIO(upstream), mode='r:gz') as original:
            tops = {PurePosixPath(m.name).parts[0] for m in original.getmembers()}
            assert len(tops) == 1
            root = next(iter(tops))
            for item in component['notices']:
                if item['source'] == 'Simplify-MIT.txt':
                    raw = src.extractfile('packaging/research/notices/fast-quadric-2019-MIT.txt').read()
                else:
                    raw = original.extractfile(root + '/' + item['source']).read()
                    if item['kind'] == 'first-comment': raw = first_comment(raw)
                target = item['target']
                meta = [value for key, value in info.items() if key.startswith('info/licenses/') and PurePosixPath(key).name == target]
                assert raw == payload['share/licenses/dem2mesh/' + target] and len(meta) == 1 and raw == meta[0], target
        notice('Verified source manifest entries: ' + str(len(manifest['files'])) + '; all ' + str(len(component['notices'])) + ' declared notice bytes matched payload and metadata')
    notice('Package audit: ' + json.dumps(result, sort_keys=True))
    retest = subprocess.run(['rattler-build', 'test', '--package-file', str(package), '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(Path(temp)/'test'), '--log-style', 'plain'], text=True, capture_output=True)
    if retest.returncode:
        notice('Fresh retest failed: ' + (retest.stderr or retest.stdout)[-1200:])
        retest.check_returncode()
    notice('Independent fresh isolated retest PASS')
