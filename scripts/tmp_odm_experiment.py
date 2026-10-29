"""Disposable CI-only ODM prototype experiment. Never upload outputs."""
import hashlib
import os
import subprocess
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

sys.excepthook = lambda typ, value, tb: print('::error::' + ' '.join(traceback.format_exception(typ, value, tb)).replace('\n', ' | '), flush=True)
ARTIFACTS = [
    ('fpcfilter', 12738542528, 'eb87588a45ce85aeed822391108faf80a75dae45506c6042cf21180ab141d262'),
    ('dem2points', 12911564893, '2e6af14e3eaffa0631c59e875fa114b95376f17a1c7c7de4815e9fc3e7eefb87'),
    ('odm-orthophoto', 12910914634, 'fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'),
    ('fastrasterfilter', 12910914634, 'fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'),
    ('renderdem', 12910914634, 'fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'),
    ('poissonrecon-odm', 12889646994, '44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf'),
    ('mvs-texturing-odm', 12841144045, '5a92c91c65b56433766eddb739f5db488d4c0cf8403647274aee262c26bdd899'),
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
        for component in ('opensfm', 'openmvs'):
            run(['python', ROOT/'scripts/check_open_research_sources.py', component, '--cache', root/'source-cache'])
            out = root / ('build-'+component)
            run(['rattler-build', 'build', '--recipe', ROOT/'research/recipes'/f'{component}-odm'/'recipe.yaml', '--target-platform', 'linux-64', '--variant-config', ROOT/'recipes/variants.yaml', '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', out, '--log-style', 'plain'])
            matches = list((out/'linux-64').glob(f'{component}-odm-*.conda'))
            assert len(matches) == 1, (component, matches)
            p = matches[0]
            run(['rattler-build', 'test', '--package-file', p, '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', root/('retest-'+component), '--log-style', 'plain'])
            run(['python', ROOT/'scripts/audit_open_research.py', f'{component}-odm', p])
            packages.append(p)
            print(f'::notice::Built {p.name} SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}', flush=True)
        project = root/'environment'
        run(['pixi', 'init', '--format', 'pixi', '--scm', 'github', '--channel', 'conda-forge', '--platform', 'linux-64', project])
        cmd=['pixi', 'add', '--manifest-path', project/'pixi.toml', *packages, 'pdal', 'python-pdal', 'gdal', 'exiftool']
        result=subprocess.run(list(map(str,cmd)), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout, flush=True)
        if result.returncode:
            print('::error::Combined solve/install failed: '+result.stdout[:9000].replace('\n',' | '), flush=True)
            raise RuntimeError('Combined environment solve/install failed')
        selected=subprocess.run(['pixi','list','--manifest-path',str(project/'pixi.toml'),'--locked'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
        print('::notice::Nine-package environment installed; selected dependencies: '+' | '.join(x.strip() for x in selected.splitlines() if any(y in x for y in ('libgdal-core','libpdal-core','libopencv','py-opencv','python-pdal'))),flush=True)
        prefix = project/'.pixi/envs/default'
        cmd=['python',ROOT/'scripts/odm_local_prototype.py','check','--prefix',prefix,'--imports']
        result=subprocess.run(list(map(str,cmd)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::Prototype preflight failed: '+result.stdout[-5000:].replace('\n',' | '),flush=True)
            raise RuntimeError('Prototype preflight failed')
        print('::notice::Combined prefix preflight and selected imports PASS', flush=True)
        archive=root/'odm.tar.gz'
        run(['curl', '--fail', '--location', 'https://codeload.github.com/OpenDroneMap/ODM/tar.gz/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45', '--output', archive])
        app=root/'odm-app'
        run(['python', ROOT/'scripts/odm_local_prototype.py', 'prepare', '--archive', archive, '--output', app])
        launch=['python', ROOT/'scripts/odm_local_prototype.py', 'run', '--app', app, '--prefix', prefix, '--', '--fast-orthophoto']
        captured([*launch, '--help'])
        print('::notice::Prototype launcher help PASS', flush=True)
        data=root/'dataset-source'
        run(['git', 'init', data])
        run(['git', '-C', data, 'fetch', '--depth=1', 'https://github.com/OpenDroneMap/odm_data_seneca.git', '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'])
        run(['git', '-C', data, 'checkout', '--detach', 'FETCH_HEAD'])
        assert subprocess.check_output(['git','-C',str(data),'rev-parse','HEAD'],text=True).strip() == '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
        projects=root/'projects'; projects.mkdir(); data.rename(projects/'seneca')
        captured([*launch, '--skip-3dmodel', '--project-path', projects, 'seneca'])
        print('::notice::Candidate dataset fast-orthophoto command completed; outputs not independently reviewed and not retained', flush=True)

if __name__ == '__main__': main()
