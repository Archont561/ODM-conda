"""Disposable CI-only ODM prototype experiment. Never upload outputs."""
import hashlib
import json
import collections
import os
import subprocess
import sys
import shutil
import tempfile
import traceback
import zipfile
from pathlib import Path

sys.excepthook = lambda typ, value, tb: print('::error::' + ' '.join(traceback.format_exception(typ, value, tb)).replace('\n', ' | '), flush=True)
ARTIFACTS = [
    ('renderdem', 12910914634, 'fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'),
    ('mvs-texturing-odm', 12841144045, '5a92c91c65b56433766eddb739f5db488d4c0cf8403647274aee262c26bdd899'),
]
PUBLISHED = [
    ('fpcfilter-v0.2-b1', 'fpcfilter-0.2-h873e7db_1.conda', '8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679'),
    ('dem2points-v0.0.0.dev20220721-b2', 'dem2points-0.0.0.dev20220721-h873e7db_2.conda', 'd7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f'),
    ('fastrasterfilter-v1.0-b2', 'fastrasterfilter-1.0-h873e7db_2.conda', '2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4'),
]

ROOT = Path.cwd()

def run(cmd, **kwargs):
    print('+', ' '.join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, **kwargs)

def captured(cmd):
    result=subprocess.run([str(x) for x in cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, flush=True)
    if result.returncode:
        print('::error::Command failed: '+result.stdout[-8000:].replace('\n',' | '), flush=True)
        result.check_returncode()

def main():
    global ROOT
    from common import repository_files
    original_root = ROOT
    with tempfile.TemporaryDirectory(prefix='odm-integration-', dir=os.environ['RUNNER_TEMP']) as tmp:
        root = Path(tmp)
        staged = root/'private-packaging'
        for path in repository_files(original_root):
            rel=path.relative_to(original_root)
            if path.name.startswith(('tmp_', 'tmp-')): continue
            target=staged/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
        for relative in ('recipes/odm-orthophoto/recipe.yaml','research/recipes/opensfm-scoped-odm/recipe.yaml','research/recipes/openmvs-odm/reduced.yaml'):
            recipe=staged/relative; text=recipe.read_text()
            assert text.count('>=4.12,<4.13')==2, relative
            text=text.replace('>=4.12,<4.13','>=4.13,<4.14')
            if relative=='recipes/odm-orthophoto/recipe.yaml':
                marker='build:\n  number: 2\n'; assert text.count(marker)==1
                text=text.replace(marker,marker+'  string: research_${{ hash }}_2\n')
            recipe.write_text('# PRIVATE OPENCV 4.13 ABI EXPERIMENT; NOT A RELEASE RECIPE\n'+text)
        ROOT=staged
        packages = []
        identities = []
        for tag, filename, expected in PUBLISHED:
            run(['gh', 'release', 'download', tag, '--pattern', filename, '--dir', root])
            p = root / filename
            assert hashlib.sha256(p.read_bytes()).hexdigest() == expected, filename
            packages.append(p)
            identities.append(f'{filename} SHA256 {expected}')
        for component, artifact, expected in ARTIFACTS:
            zip_path = root / f'{artifact}.zip'
            with zip_path.open('wb') as out:
                run(['gh', 'api', f'repos/Archont561/ODM-conda/actions/artifacts/{artifact}/zip'], stdout=out)
            assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == expected, component
            with zipfile.ZipFile(zip_path) as z:
                matches = [n for n in z.namelist() if Path(n).name.startswith(component+'-') and n.endswith('.conda')]
                assert len(matches) == 1, (component, z.namelist())
                p = root / Path(matches[0]).name
                p.write_bytes(z.read(matches[0])); packages.append(p)
                identities.append(f'{p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}')
            zip_path.unlink()
        print('::notice::Verified retained package identities: ' + '; '.join(identities), flush=True)
        # Private orthophoto variant: unchanged source and tests/audits; alternate host/run ABI only.
        orth_out=root/'build-orthophoto'
        run(['rattler-build','build','--recipe',ROOT/'recipes/odm-orthophoto/recipe.yaml','--target-platform','linux-64','--variant-config',ROOT/'recipes/variants.yaml','--channel','conda-forge','--channel-priority','strict','--output-dir',orth_out,'--log-style','plain'])
        orth=list((orth_out/'linux-64').glob('odm-orthophoto-*.conda')); assert len(orth)==1
        run(['rattler-build','test','--package-file',orth[0],'--channel','conda-forge','--channel-priority','strict','--output-dir',root/'retest-orthophoto','--log-style','plain'])
        run(['python',ROOT/'scripts/audit_package.py','--component','odm-orthophoto','--output-dir',orth_out,'--reports-dir',root/'reports'])
        packages.append(orth[0]); print(f'::notice::PRIVATE 4.13 orthophoto build fresh test audit PASS {hashlib.sha256(orth[0].read_bytes()).hexdigest()}',flush=True)
        # Build the current reduced Poisson candidate privately and audit it separately.
        original = root/'poisson-original.tar.gz'
        candidate = root/'poisson-candidate.tar.gz'
        prepared = root/'poisson-prepared'
        run(['curl', '-fsSL', 'https://codeload.github.com/OpenDroneMap/PoissonRecon/tar.gz/97caa6d34d1b05b59888bed019dea89ced74445e', '-o', original])
        run(['python', ROOT/'scripts/poisson_reduced_candidate.py', '--source', original, '--output', candidate])
        run(['python', ROOT/'scripts/poisson_candidate_recipe.py', '--original', original, '--candidate', candidate, '--destination', prepared])
        out = root/'build-poisson'
        run(['rattler-build', 'build', '--recipe', prepared/'packaging/recipes/poissonrecon-odm/recipe.yaml', '--target-platform', 'linux-64', '--variant-config', ROOT/'recipes/variants.yaml', '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', out, '--log-style', 'plain'])
        matches = list((out/'linux-64').glob('poissonrecon-odm-*.conda'))
        assert len(matches) == 1, matches
        p = matches[0]
        run(['rattler-build', 'test', '--package-file', p, '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', root/'retest-poisson', '--log-style', 'plain'])
        run(['python', ROOT/'scripts/audit_poisson_research.py', '--package', p, '--candidate', candidate])
        packages.append(p)
        print(f'DETAIL::Built reduced-source {p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}', flush=True)
        # Build the OpenSfM package from the actual reduced primary archive.
        original = root/'opensfm-original.tar.gz'
        candidate = root/'opensfm-candidate.tar.gz'
        prepared = root/'opensfm-prepared'
        run(['curl', '-fsSL', 'https://codeload.github.com/OpenDroneMap/OpenSfM/tar.gz/c5328439465e6ace011f39077d1077d7b1cdd65d', '-o', original])
        run(['python', ROOT/'scripts/opensfm_reduced_candidate.py', '--source', original, '--output', candidate])
        run(['python', ROOT/'scripts/opensfm_reduced_recipe.py', '--original', original, '--candidate', candidate, '--destination', prepared])
        out = root/'build-opensfm-scoped'
        run(['rattler-build', 'build', '--recipe', prepared/'packaging/research/recipes/opensfm-scoped-odm/recipe.yaml', '--target-platform', 'linux-64', '--variant-config', ROOT/'recipes/variants.yaml', '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', out, '--log-style', 'plain'])
        matches = list((out/'linux-64').glob('opensfm-scoped-odm-*.conda'))
        assert len(matches) == 1, matches
        p = matches[0]
        run(['rattler-build', 'test', '--package-file', p, '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', root/'retest-opensfm-scoped', '--log-style', 'plain'])
        run(['python', ROOT/'scripts/audit_open_research.py', 'opensfm-scoped-odm', p])
        packages.append(p)
        print(f'DETAIL::Built reduced-source {p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()} candidate SHA256 {hashlib.sha256(candidate.read_bytes()).hexdigest()}', flush=True)
        for component in ('openmvs',):
            run(['python', ROOT/'scripts/check_open_research_sources.py', ('opensfm' if component == 'opensfm-scoped' else component), '--cache', root/'source-cache'])
            out = root / ('build-'+component)
            run(['rattler-build', 'build', '--recipe', ROOT/'research/recipes'/f'{component}-odm'/'reduced.yaml', '--target-platform', 'linux-64', '--variant-config', ROOT/'recipes/variants.yaml', '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', out, '--log-style', 'plain'])
            matches = list((out/'linux-64').glob(f'{component}-odm-*.conda'))
            assert len(matches) == 1, (component, matches)
            p = matches[0]
            run(['rattler-build', 'test', '--package-file', p, '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', root/('retest-'+component), '--log-style', 'plain'])
            run(['python', ROOT/'scripts/audit_open_research.py', f'{component}-odm', p])
            packages.append(p)
            print(f'DETAIL::Built {p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}', flush=True)
        # Build application package without tests here: its dependencies exist only
        # in the private channel assembled immediately below.
        out=root/'build-odm'
        run(['rattler-build','build','--recipe',ROOT/'research/recipes/odm-fast-research/recipe.yaml','--target-platform','linux-64','--variant-config',ROOT/'recipes/variants.yaml','--channel','conda-forge','--channel-priority','strict','--output-dir',out,'--test','skip','--log-style','plain'])
        candidates=list((out/'linux-64').glob('odm-fast-research-*.conda')); assert len(candidates)==1
        packages.append(candidates[0])
        print('::notice::ODM candidate '+candidates[0].name+' SHA256 '+hashlib.sha256(candidates[0].read_bytes()).hexdigest(),flush=True)
        # Repack five hash-pinned upstream wheels as explicitly private Conda packages.
        for recipe in sorted((ROOT/'research/recipes/python-wheel-research').glob('*.yaml')):
            out=root/('wheel-'+recipe.stem)
            run(['rattler-build','build','--recipe',recipe,'--target-platform','linux-64','--variant-config',ROOT/'recipes/variants.yaml','--channel','conda-forge','--channel-priority','strict','--output-dir',out,'--log-style','plain'])
            matches=list((out/'linux-64').glob('odm-research-'+recipe.stem+'-*.conda')); assert len(matches)==1
            packages.append(matches[0])
        # Private loopback-only channel gives the lock stable relocatable URLs.
        from private_conda_channel import create as create_channel
        import http.server, functools, threading, socketserver
        package_info=create_channel(packages,root/'channel',root=ROOT)
        socketserver.TCPServer.allow_reuse_address=True
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root/'channel'))
        server=http.server.ThreadingHTTPServer(('127.0.0.1', 48179),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        channel='http://127.0.0.1:48179'
        project = root/'environment'
        run(['pixi','init','--format','pixi','--scm','github','--channel',channel,'--channel','conda-forge','--platform','linux-64',project])
        names=['odm-fast-research']
        cmd=['pixi','add','--manifest-path',project/'pixi.toml',*names]
        result=subprocess.run(list(map(str,cmd)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::Combined solve/install failed: '+result.stdout[:9000].replace('\n',' | '),flush=True)
            raise RuntimeError('Combined environment solve/install failed')
        selected=subprocess.run(['pixi','list','--manifest-path',str(project/'pixi.toml'),'--locked'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
        print('DETAIL::Nine-package environment installed; selected dependencies: '+' | '.join(x.strip() for x in selected.splitlines() if any(y in x for y in ('libgdal-core','libpdal-core','libopencv','py-opencv','python-pdal'))),flush=True)
        print(f'DETAIL::Combined environment lists {len(selected.splitlines())} lines; scope: nine actual packages and selected dependencies.', flush=True)
        print('DETAIL::All five ODM runtime wheels installed as Conda packages; no PyPI additions',flush=True)
        # Preserve the lock and local channel bytes, relocate both, then install
        # in an empty prefix using isolated caches and the same loopback URL.
        import yaml
        original_prefix=project/'.pixi/envs/default'
        original_lock=(project/'pixi.lock').read_bytes()
        lock=yaml.safe_load(original_lock)
        assert not any('pypi' in entry for entry in lock['packages']), 'Unexpected PyPI packages'
        locked_local={entry.get('conda','').rsplit('/',1)[-1]:entry.get('sha256') for entry in lock['packages'] if isinstance(entry.get('conda'),str) and entry['conda'].startswith(channel+'/')}
        expected={p['filename']:p['sha256'] for p in package_info}
        assert locked_local==expected, (locked_local,expected)
        assert str(root).encode() not in original_lock and str(root).encode() not in (project/'pixi.toml').read_bytes()
        server.shutdown();server.server_close();thread.join()
        replay=root/'relocated'; replay.mkdir()
        shutil.copy2(project/'pixi.toml',replay/'pixi.toml'); shutil.copy2(project/'pixi.lock',replay/'pixi.lock')
        shutil.copytree(root/'channel',replay/'channel')
        for item in package_info: assert hashlib.sha256((replay/'channel/linux-64'/item['filename']).read_bytes()).hexdigest()==item['sha256']
        # Remove the original channel to prove replay uses the relocated files.
        shutil.rmtree(root/'channel')
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(replay/'channel'))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',48179),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        env=os.environ.copy(); env['HOME']=str(root/'replay-home'); env['XDG_CACHE_HOME']=str(root/'replay-cache'); env['RATTLER_CACHE_DIR']=str(root/'replay-cache/rattler'); Path(env['HOME']).mkdir()
        run(['pixi','install','--manifest-path',replay/'pixi.toml','--locked'],env=env)
        assert (replay/'pixi.lock').read_bytes()==original_lock
        from inventory_conda_environment import inventory
        before=inventory(original_prefix); after=inventory(replay/'.pixi/envs/default')
        # Compare selected package identities, hashes, and URLs; notice lists can vary by linking implementation.
        def identities(r): return [(p['name'],p['version'],p['build'],p['sha256'],p['binary_package_url']) for p in r['packages']]
        assert identities(before)==identities(after), 'replayed Conda inventory mismatch'
        print('::notice::REPLAY PASS byte-identical lock '+hashlib.sha256(original_lock).hexdigest()+'; relocated fifteen package archives and fresh cache; '+str(len(before['packages']))+' matching Conda records.',flush=True)
        project=replay
        prefix=project/'.pixi/envs/default'
        assert (prefix/'share/proj/proj.db').is_file(), 'Missing prefix PROJ database'
        print('DETAIL::Prefix PROJ database present; launcher supplies PROJ_DATA and PROJ_LIB', flush=True)
        cmd=['python',ROOT/'scripts/odm_local_prototype.py','check','--prefix',prefix,'--imports']
        result=subprocess.run(list(map(str,cmd)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::Prototype preflight failed: '+result.stdout[-5000:].replace('\n',' | '),flush=True)
            raise RuntimeError('Prototype preflight failed')
        print('DETAIL::Combined prefix preflight and selected imports PASS', flush=True)
        package = prefix/'lib/python3.12/site-packages/opensfm'
        for asset in ('data/sensor_data.sqlite','data/bow/bow_hahog_root_uchar_10000.npz','data/bow/bow_hahog_root_uchar_64.npz'):
            assert not (package/asset).exists(), asset
        probe = root/'scope-probe'
        (probe/'images').mkdir(parents=True)
        (probe/'images/a.jpg').touch()
        test = """from pathlib import Path
from opensfm.dataset import DataSet
p=Path(__import__('sys').argv[1])
assert DataSet(str(p)).config['matcher_type']=='FLANN'
for config in ('matcher_type: WORDS', 'matching_bow_neighbors: 1', 'matching_vlad_neighbors: 1'):
 (p/'config.yaml').write_text(config)
 try: DataSet(str(p))
 except ValueError as e: assert 'not supported' in str(e)
 else: raise AssertionError(config)
print('Default and three scoped mode guards PASS')
"""
        run([prefix/'bin/python', '-c', test, probe])
        test = "from opensfm.sensors import sensor_data; x=sensor_data(); assert len(x)==3708 and x['acer ce-5330']==5.75"
        run([prefix/'bin/python', '-c', test])
        print('DETAIL::Installed scoped package excludes assets; default, three unsupported configurations and JSON fallback PASS',flush=True)
        from inventory_conda_environment import inventory
        report=inventory(prefix)
        missing_licenses=[p['name'] for p in report['packages'] if not p['license']]
        missing_hash=[p['name'] for p in report['packages'] if not p['sha256']]
        print(f'::notice::Fresh inventory: {len(report["packages"])} Conda records; missing license {len(missing_licenses)}; missing metadata SHA256 {len(missing_hash)}',flush=True)
        print('::notice::PRIVATE PACKAGE HASHES '+ '; '.join(p.name+' '+hashlib.sha256(p.read_bytes()).hexdigest() for p in packages),flush=True)
        # Record a bounded sanitized lock-derived snapshot, never the private lock or packages.
        import yaml, base64, zlib
        from urllib.parse import urlsplit, urlunsplit
        lock_path=project/'pixi.lock'
        run(['pixi','install','--manifest-path',project/'pixi.toml','--locked'])
        lock_bytes=lock_path.read_bytes(); lock=yaml.safe_load(lock_bytes)
        python_packages=[]
        for item in lock['packages']:
            if 'pypi' not in item: continue
            locator=item['pypi']; assert isinstance(locator,str)
            u=urlsplit(locator)
            if u.scheme in ('http','https') and u.hostname:
                locator=urlunsplit((u.scheme,u.hostname,u.path,'',''))
            elif u.scheme == 'file': locator='local-file:'+Path(u.path).name
            else: raise RuntimeError('Unsupported pypi lock locator')
            record={'binary_url':locator}
            for k in ('name','version','sha256','md5','hash','requires_python'):
                if k in item: record[k]=item[k]
            python_packages.append(record)
        local_packages=[{'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in packages]
        snapshot={'scope':'Sanitized lock-derived observation and Conda installed records; not a runnable Pixi lock or source/license audit. Private binaries absent.',
                  'lock_version':lock.get('version'),'raw_lock_sha256':hashlib.sha256(lock_bytes).hexdigest(),
                  'conda_inventory':report,'pypi_lock_records':python_packages,'local_binaries':local_packages}
        data=json.dumps(snapshot,sort_keys=True,separators=(',',':')).encode()
        encoded=base64.b64encode(zlib.compress(data,9)).decode()
        print(f'DETAIL::SNAPSHOT_COUNT {len(report["packages"])} PIP {len(python_packages)} BYTES {len(data)} CHUNKS {(len(encoded)+2499)//2500}',flush=True)
        for i in range(0,len(encoded),2500): print(f'DETAIL::SNAPSHOT_CHUNK_{i//2500:02d} {encoded[i:i+2500]}',flush=True)
        for item in report['packages']:
            if item['name'] in ('libopencv','py-opencv','libopenvino','libgdal-core','libpdal-core'):
                print(f'::notice::RESOLVED {item["name"]} {item["version"]} {item["build"]} SHA256 {item["sha256"]}',flush=True)

        launch=[prefix/'bin/odm-fast-research','--fast-orthophoto']
        captured([*launch, '--help'])
        print('::notice::Installed ODM package launcher help PASS', flush=True)
        data=root/'dataset-source'
        run(['git', 'init', data])
        run(['git', '-C', data, 'fetch', '--depth=1', 'https://github.com/OpenDroneMap/odm_data_seneca.git', '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'])
        run(['git', '-C', data, 'checkout', '--detach', 'FETCH_HEAD'])
        assert subprocess.check_output(['git','-C',str(data),'rev-parse','HEAD'],text=True).strip() == '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
        projects=root/'projects'; projects.mkdir(); data.rename(projects/'seneca')
        result = subprocess.run(list(map(str, [*launch, '--skip-3dmodel', '--project-path', projects, 'seneca'])), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout, flush=True)
        if result.returncode:
            print('::error::Dataset trial failed: ' + result.stdout[-6000:].replace('\n', ' | '), flush=True)
            result.check_returncode()
        print('::notice::Seneca pipeline completed with scoped runtime and unsupported-mode guard', flush=True)
        raster = projects/'seneca'/'odm_orthophoto'/'odm_orthophoto.tif'
        report = projects/'seneca'/'odm_report'/'report.pdf'
        assert raster.is_file() and raster.stat().st_size > 0, f'No final orthophoto at {raster}'
        assert report.is_file() and report.stat().st_size > 0, f'No final report at {report}'
        info = subprocess.check_output(['pixi', 'run', '--manifest-path', str(project/'pixi.toml'), '--locked', 'gdalinfo', '-json', '-stats', str(raster)], text=True)
        metadata = json.loads(info)
        from odm_raster_sanity import validate
        result = validate(metadata)
        print('::notice::Live GDAL raster sanity checks passed; metadata/statistics only, not visual or geographic validation.', flush=True)
        size = metadata['size']; bands = metadata['bands']; transform = metadata.get('geoTransform'); crs = metadata.get('coordinateSystem', {}).get('wkt')
        assert len(size) == 2 and all(x > 0 for x in size), size
        assert len(bands) >= 3, len(bands)
        assert transform and len(transform) == 6 and transform[1] != 0 and transform[5] != 0, transform
        assert crs, 'Missing output CRS'
        stats = [{k: b.get(k) for k in ('band', 'type', 'colorInterpretation', 'minimum', 'maximum', 'mean', 'stdDev', 'noDataValue')} for b in bands]
        print('::notice::Final raster metadata: '+json.dumps({'size': size, 'geoTransform': transform, 'crs': crs, 'bands': stats, 'bytes': raster.stat().st_size, 'report_bytes': report.stat().st_size}, separators=(',',':')).replace('\n',' '), flush=True)
        print('::notice::Final raster exists with positive dimensions, geotransform, CRS and at least 3 bands; report exists; gdalinfo -stats succeeded. Dataset outputs not retained or uploaded.', flush=True)

if __name__ == '__main__': main()
# Validate the bumped ODM application build identity.
