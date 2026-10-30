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
    ('odm-orthophoto-v0.0.0.dev20250225-b2', 'odm-orthophoto-0.0.0.dev20250225-h873e7db_2.conda', 'c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614'),
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
    with tempfile.TemporaryDirectory(prefix='odm-integration-', dir=os.environ['RUNNER_TEMP']) as tmp:
        root = Path(tmp)
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
        project = root/'environment'
        run(['pixi', 'init', '--format', 'pixi', '--scm', 'github', '--channel', 'conda-forge', '--platform', 'linux-64', project])
        cmd=['pixi', 'add', '--manifest-path', project/'pixi.toml', *packages, 'pdal', 'python-pdal', 'gdal', 'exiftool', 'scikit-image', 'scikit-learn', 'shapely', 'fiona', 'edt', 'piexif', 'trimesh', 'onnxruntime', 'packaging', 'libopenvino >=2026.0']
        result=subprocess.run(list(map(str,cmd)), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout, flush=True)
        if result.returncode:
            print('::error::Combined solve/install failed: '+result.stdout[:9000].replace('\n',' | '), flush=True)
            raise RuntimeError('Combined environment solve/install failed')
        selected=subprocess.run(['pixi','list','--manifest-path',str(project/'pixi.toml'),'--locked'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
        print('DETAIL::Nine-package environment installed; selected dependencies: '+' | '.join(x.strip() for x in selected.splitlines() if any(y in x for y in ('libgdal-core','libpdal-core','libopencv','py-opencv','python-pdal'))),flush=True)
        print(f'DETAIL::Combined environment lists {len(selected.splitlines())} lines; scope: nine actual packages and selected dependencies.', flush=True)
        captured(['pixi','add','--manifest-path',project/'pixi.toml','--pypi','pyodm==1.5.12','pysolar==0.13','pillow-jxl-plugin==1.3.4','pygltflib==1.16.5','codem==0.26.1'])
        prefix = project/'.pixi/envs/default'
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
        print('::notice::LOCAL_BINARIES ' + '; '.join(p.name+' '+hashlib.sha256(p.read_bytes()).hexdigest() for p in packages), flush=True)
        # Inspect exact solver-selected OpenVINO package info metadata after independently hashing archives.
        import urllib.request, tarfile, io, zstandard
        selected_vino = [p for p in report['packages'] if p['name'].startswith('libopenvino')]
        assert selected_vino and all(p['version'] >= '2026.0' for p in selected_vino)
        results=[]
        for item in selected_vino:
            url=item['binary_package_url']; expected=item['sha256']
            assert url and url.startswith('https://conda.anaconda.org/conda-forge/') and expected
            with urllib.request.urlopen(url) as response:
                data=response.read()
            assert hashlib.sha256(data).hexdigest()==expected
            with zipfile.ZipFile(io.BytesIO(data)) as outer:
                name=next(n for n in outer.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
                with tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(io.BytesIO(outer.read(name))),mode='r|') as tar:
                    license_files={}; index=None; about=None; recipe=None
                    for entry in tar:
                        if entry.isfile() and (entry.name.startswith('info/licenses/') or entry.name in ('info/index.json','info/about.json','info/recipe/meta.yaml')):
                            contents=tar.extractfile(entry).read()
                            if entry.name.startswith('info/licenses/'): license_files[entry.name]=hashlib.sha256(contents).hexdigest()
                            elif entry.name=='info/index.json': index=json.loads(contents)
                            elif entry.name=='info/about.json': about=json.loads(contents)
                            else: recipe=hashlib.sha256(contents).hexdigest()
                assert index and about
                results.append({'name':item['name'],'version':item['version'],'build':item['build'],'sha256':expected,'url':url,'index_license':index.get('license'),'about_license':about.get('license'),'feedstock_sha':about.get('extra',{}).get('sha'),'declared_license_files':about.get('license_file'),'info_licenses':license_files,'rendered_recipe_sha256':recipe})
        import zlib, base64
        encoded=base64.b64encode(zlib.compress(json.dumps(results,sort_keys=True,separators=(',',':')).encode(),9)).decode()
        print('DETAIL::OPENVINO_RESULT_CHUNKS '+str((len(encoded)+2999)//3000),flush=True)
        for i in range(0,len(encoded),3000): print(f'DETAIL::OPENVINO_CHUNK_{i//3000:02d} {encoded[i:i+3000]}',flush=True)
        print(f'::notice::OPENVINO_INSPECTED {len(results)} packages; versions '+','.join(sorted(set(x['version'] for x in results)))+f'; license fields {sum(bool(x["index_license"]) for x in results)}; info/licenses files {sum(bool(x["info_licenses"]) for x in results)}',flush=True)
        archive=root/'odm.tar.gz'
        run(['curl', '--fail', '--location', 'https://codeload.github.com/OpenDroneMap/ODM/tar.gz/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45', '--output', archive])
        app=root/'odm-app'
        run(['python', ROOT/'scripts/odm_local_prototype.py', 'prepare', '--archive', archive, '--output', app])
        launch=['python', ROOT/'scripts/odm_local_prototype.py', 'run', '--app', app, '--prefix', prefix, '--', '--fast-orthophoto']
        captured([*launch, '--help'])
        print('DETAIL::Prototype launcher help PASS', flush=True)
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
