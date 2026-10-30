#!/usr/bin/env python3
"""Build and replay a private ODM research bundle; never upload or publish it.

A bundle is an exact *binary* replay input, not a source-completeness offer.
It must remain under the owner's access control and is linux-64 only.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import platform
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import urllib.request
from contextlib import contextmanager
from pathlib import Path

import yaml
from common import ROOT, ScaffoldError, config, fail_cli, rattler, run, sha256
from private_conda_channel import create as create_channel

PORT = 48179
BASE = ('fpcfilter', 'dem2points', 'fastrasterfilter', 'renderdem', 'mvs-texturing-odm')


def validate_destination(path: Path, root: Path = ROOT) -> None:
    path = Path(path)
    if path.exists() or path.is_symlink() or not path.parent.is_dir() or path.resolve().is_relative_to(Path(root).resolve()):
        raise ScaffoldError('Destination must be new, outside the repository and have an existing parent')


def bundle_files(bundle: Path) -> list[Path]:
    fixed = [bundle/'pixi.toml', bundle/'pixi.lock', bundle/'channel/linux-64/repodata.json', bundle/'channel/noarch/repodata.json']
    files = fixed + sorted((bundle/'channel/linux-64').glob('*.conda'))
    channel=bundle/'channel'
    if any(p.is_symlink() for p in [channel, channel/'linux-64', channel/'noarch']):
        raise ScaffoldError('Unsafe private channel directory')
    if len(files) == len(fixed) or any(p.is_symlink() or not p.is_file() for p in files):
        raise ScaffoldError('Missing or unsafe private bundle file')
    found = {p for p in channel.rglob('*') if p.is_file() or p.is_symlink()}
    if found != set(files[2:]):
        raise ScaffoldError('Unexpected private channel files')
    return files


def seal(bundle: Path, port: int) -> None:
    if not 1 <= port <= 65535:
        raise ScaffoldError('Invalid loopback port')
    files = bundle_files(bundle)
    record = {'schema_version': 1, 'port': port, 'scope': 'private-research-only',
              'files': {p.relative_to(bundle).as_posix(): sha256(p) for p in files}}
    (bundle/'private-bundle.json').write_text(json.dumps(record, sort_keys=True, indent=2)+'\n')


def verify(bundle: Path, *, expected_manifest_sha: str | None = None) -> int:
    bundle = Path(bundle)
    manifest = bundle/'private-bundle.json'
    if bundle.is_symlink() or not bundle.is_dir() or manifest.is_symlink() or not manifest.is_file():
        raise ScaffoldError('Missing or unsafe private bundle')
    if expected_manifest_sha is not None and (not re.fullmatch(r'[a-f0-9]{64}', expected_manifest_sha) or sha256(manifest) != expected_manifest_sha):
        raise ScaffoldError('Private bundle manifest checksum mismatch')
    data = json.loads(manifest.read_text())
    if data.get('schema_version') != 1 or data.get('scope') != 'private-research-only' or type(data.get('port')) is not int or not 1 <= data['port'] <= 65535 or not isinstance(data.get('files'), dict):
        raise ScaffoldError('Invalid private bundle manifest')
    files = bundle_files(bundle)
    actual = {p.relative_to(bundle).as_posix(): p for p in files}
    if set(actual) != set(data['files']):
        raise ScaffoldError('Missing or unexpected private bundle files')
    if any(sha256(p) != data['files'][name] for name,p in actual.items()):
        raise ScaffoldError('Private bundle checksum mismatch')
    return data['port']


@contextmanager
def loopback(directory: Path, port: int):
    class Server(http.server.ThreadingHTTPServer):
        allow_reuse_address = True
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    server = Server(('127.0.0.1', port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        yield f'http://127.0.0.1:{port}'
    finally:
        server.shutdown(); server.server_close(); thread.join()


def build_recipe(recipe: Path, name: str, work: Path, *, skip_tests: bool = False) -> Path:
    output=work/'output'; output.mkdir(parents=True)
    cmd=[rattler(), 'build', '--recipe', str(recipe), '--target-platform', 'linux-64', '--variant-config', str(ROOT/'recipes/variants.yaml'), '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(output), '--log-style', 'plain']
    if skip_tests: cmd += ['--test', 'skip']
    run(cmd)
    matches=list((output/'linux-64').glob(name+'-*.conda'))
    if len(matches) != 1: raise ScaffoldError(f'Expected one private package for {name}')
    package=matches[0]
    if not skip_tests:
        run([rattler(), 'test', '--package-file', str(package), '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(work/'retest'), '--log-style', 'plain'])
    return package


def download_sdist(url: str, expected: str, target: Path) -> None:
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != 'files.pythonhosted.org' or parsed.username or parsed.password or not re.fullmatch(r'[a-f0-9]{64}', expected):
        raise ScaffoldError('Unexpected pinned sdist URL or digest')
    request=urllib.request.Request(url,headers={'User-Agent':'ODM-conda-private-research/1'})
    with urllib.request.urlopen(request,timeout=90) as response, target.open('xb') as output:
        if urllib.parse.urlsplit(response.url).scheme != 'https': raise ScaffoldError('Unsafe sdist redirect')
        total=0
        while block := response.read(1024*1024):
            total += len(block)
            if total > 512*1024*1024: raise ScaffoldError('Source archive too large')
            output.write(block)
    if sha256(target) != expected: raise ScaffoldError('Downloaded sdist checksum mismatch')


def private_identity(recipe: Path, build_number: int) -> None:
    text=recipe.read_text(); marker=f'build:\n  number: {build_number}\n'
    if text.count(marker) != 1: raise ScaffoldError(f'Unexpected recipe identity: {recipe.name}')
    recipe.write_text(text.replace(marker, marker+f'  string: research_${{{{ hash }}}}_{build_number}\n'))


def build_packages(work: Path) -> list[Path]:
    from prepare_opencv413_research import prepare
    from source_bundle import graph_archives
    from common import fetch_pinned_archive
    from opensfm_graph_policy import PRIMARY
    from opensfm_reduced_candidate import make_candidate as opensfm_candidate
    from opensfm_reduced_recipe import prepare as opensfm_prepare
    from poisson_reduced_candidate import make_candidate as poisson_candidate
    from poisson_candidate_recipe import prepare as poisson_prepare
    from prepare_jxl_source import prepare as jxl_prepare

    staged=work/'packaging'; prepare(staged)
    components=config()['components']; packages=[]
    for name in BASE:
        component=components[name]; recipe=staged/component['recipe']
        private_identity(recipe,component['build_number'])
        if component['source'].get('additional_sources'):
            graph_archives(name,component['source'],work/'source-cache')
        package=build_recipe(recipe,name,work/('base-'+name))
        run([sys.executable, str(ROOT/'scripts/audit_package.py'), '--component', name, '--output-dir', str(package.parent.parent), '--reports-dir', str(work/'reports')])
        packages.append(package)
    orth=build_recipe(staged/'recipes/odm-orthophoto/recipe.yaml','odm-orthophoto',work/'orthophoto')
    run([sys.executable,str(ROOT/'scripts/audit_package.py'),'--component','odm-orthophoto','--output-dir',str(orth.parent.parent),'--reports-dir',str(work/'reports')]); packages.append(orth)
    original=fetch_pinned_archive('poissonrecon',components['poissonrecon-odm']['source'],work/'source-cache')
    candidate=work/'poisson-candidate.tar.gz'; poisson_candidate(original,candidate,root=staged)
    prepared=work/'poisson-prepared'; poisson_prepare(candidate,prepared,original,root=staged)
    package=build_recipe(prepared/'packaging/recipes/poissonrecon-odm/recipe.yaml','poissonrecon-odm',work/'poisson')
    run([sys.executable,str(ROOT/'scripts/audit_poisson_research.py'),'--package',str(package),'--candidate',str(candidate)]); packages.append(package)
    original=fetch_pinned_archive('opensfm',PRIMARY,work/'source-cache')
    candidate=work/'opensfm-candidate.tar.gz'; opensfm_candidate(original,candidate)
    prepared=work/'opensfm-prepared'; opensfm_prepare(original,candidate,prepared,root=staged)
    package=build_recipe(prepared/'packaging/research/recipes/opensfm-scoped-odm/recipe.yaml','opensfm-scoped-odm',work/'opensfm')
    run([sys.executable,str(ROOT/'scripts/audit_open_research.py'),'opensfm-scoped-odm',str(package)]); packages.append(package)
    run([sys.executable,str(ROOT/'scripts/check_open_research_sources.py'),'openmvs','--cache',str(work/'source-cache')])
    package=build_recipe(staged/'research/recipes/openmvs-odm/reduced.yaml','openmvs-odm',work/'openmvs')
    run([sys.executable,str(ROOT/'scripts/audit_open_research.py'),'openmvs-odm',str(package)]); packages.append(package)
    for template in sorted((staged/'research/recipes/python-source-research').glob('*.yaml')):
        name=template.stem; recipe=template
        if name == 'pillow-jxl-plugin':
            info=yaml.safe_load(template.read_text())['source']
            source=work/'pillow-jxl-plugin.tar.gz'; download_sdist(info['url'],info['sha256'],source)
            jxl_prepare(source,work/'jxl-prepared'); recipe=work/'jxl-prepared/recipe/recipe.yaml'
        packages.append(build_recipe(recipe,'odm-research-'+name,work/('python-'+name)))
    recipe=staged/'research/recipes/odm-fast-research/recipe.yaml'; text=recipe.read_text()
    for name in BASE:
        pattern=rf'^(    - {re.escape(name)} ==[^\n ]+)$'
        text,n=re.subn(pattern,r'\1 research_*',text,flags=re.MULTILINE)
        if n != 1: raise ScaffoldError(f'Unexpected ODM dependency for {name}')
    marker='build:\n  number: 2\n'
    if text.count(marker) != 1: raise ScaffoldError('Unexpected ODM build identity')
    recipe.write_text(text.replace(marker,'build:\n  number: 3\n'))
    packages.append(build_recipe(recipe,'odm-fast-research',work/'odm',skip_tests=True))
    if len(packages) != 15: raise ScaffoldError('Unexpected private package count')
    return packages


def replay(bundle: Path, *, dataset: Path | None = None, expected_inventory: list | None = None, expected_manifest_sha: str | None = None) -> None:
    port=verify(bundle, expected_manifest_sha=expected_manifest_sha)
    with tempfile.TemporaryDirectory(prefix='odm-private-replay-') as tmp:
        scratch=Path(tmp); project=scratch/'project'; project.mkdir()
        shutil.copy2(bundle/'pixi.toml',project/'pixi.toml'); shutil.copy2(bundle/'pixi.lock',project/'pixi.lock')
        env=os.environ.copy(); env['HOME']=str(scratch/'home'); env['XDG_CACHE_HOME']=str(scratch/'cache'); env['RATTLER_CACHE_DIR']=str(scratch/'cache/rattler'); Path(env['HOME']).mkdir()
        with loopback(bundle/'channel',port):
            run(['pixi','install','--manifest-path',str(project/'pixi.toml'),'--locked'],env=env)
            if (project/'pixi.lock').read_bytes() != (bundle/'pixi.lock').read_bytes(): raise ScaffoldError('Replay changed the lock')
            prefix=project/'.pixi/envs/default'
            if expected_inventory is not None:
                from inventory_conda_environment import inventory
                observed=[(p['name'],p['version'],p['build'],p['sha256'],p['binary_package_url']) for p in inventory(prefix)['packages']]
                if observed != expected_inventory: raise ScaffoldError('Replayed Conda inventory differs')
                print(f'PASS: {len(observed)} matching Conda identities and hashes',flush=True)
            run([str(prefix/'bin/odm-fast-research'),'--fast-orthophoto','--help'])
            if dataset is not None:
                dataset=Path(dataset).resolve()
                if not dataset.is_dir() or dataset.is_relative_to(ROOT): raise ScaffoldError('Dataset must be a directory outside the repository')
                if any(p.is_symlink() for p in dataset.rglob('*')): raise ScaffoldError('Dataset must not contain symlinks')
                projects=scratch/'projects'; projects.mkdir(); shutil.copytree(dataset,projects/'dataset',symlinks=False)
                run([str(prefix/'bin/odm-fast-research'),'--fast-orthophoto','--skip-3dmodel','--project-path',str(projects),'dataset'])
                raster=projects/'dataset/odm_orthophoto/odm_orthophoto.tif'; report=projects/'dataset/odm_report/report.pdf'
                if not raster.is_file() or not report.is_file() or not raster.stat().st_size or not report.stat().st_size: raise ScaffoldError('Dataset outputs missing')
                info=subprocess.check_output([str(prefix/'bin/gdalinfo'),'-json','-stats',str(raster)],text=True)
                from odm_raster_sanity import validate
                validate(json.loads(info))
                print('PASS: private dataset pipeline and raster sanity (outputs discarded)',flush=True)
        print('PASS: locked private replay and launcher; no release approval',flush=True)


def build(destination: Path, port: int, dataset: Path | None) -> None:
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64','amd64'): raise ScaffoldError('Private build requires linux-64')
    validate_destination(destination)
    if not 1 <= port <= 65535: raise ScaffoldError('Invalid loopback port')
    destination.mkdir(mode=0o700)
    try:
        with tempfile.TemporaryDirectory(prefix='odm-private-build-') as tmp:
            work=Path(tmp); packages=build_packages(work)
            info=create_channel(packages,destination/'channel')
            project=work/'project'
            with loopback(destination/'channel',port) as channel:
                run(['pixi','init','--format','pixi','--scm','github','--channel',channel,'--channel','conda-forge','--platform','linux-64',str(project)])
                run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'odm-fast-research'])
            lock=yaml.safe_load((project/'pixi.lock').read_text())
            if any('pypi' in item for item in lock['packages']): raise ScaffoldError('Unexpected PyPI lock entry')
            selected={item['conda'].rsplit('/',1)[-1]: item.get('sha256') for item in lock['packages'] if isinstance(item.get('conda'),str) and item['conda'].startswith(f'http://127.0.0.1:{port}/')}
            if selected != {item['filename']:item['sha256'] for item in info}: raise ScaffoldError('Lock does not select exactly the private package set')
            from inventory_conda_environment import inventory
            original=inventory(project/'.pixi/envs/default')
            identities=[(p['name'],p['version'],p['build'],p['sha256'],p['binary_package_url']) for p in original['packages']]
            for name in ('pixi.toml','pixi.lock'): shutil.copy2(project/name,destination/name)
            seal(destination,port)
            manifest_sha=sha256(destination/'private-bundle.json')
            relocated=work/'relocated-bundle'; shutil.copytree(destination,relocated)
            replay(relocated,dataset=dataset,expected_inventory=identities,expected_manifest_sha=manifest_sha)
            print(f'PASS: private bundle retained at {destination}; lock SHA256 {sha256(destination/"pixi.lock")}',flush=True)
            print(f'Record this manifest SHA256 separately for verified replay: {manifest_sha}',flush=True)
    except Exception:
        shutil.rmtree(destination,ignore_errors=True)
        raise


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='action',required=True)
    create=sub.add_parser('build'); create.add_argument('--destination',required=True,type=Path); create.add_argument('--port',type=int,default=PORT); create.add_argument('--dataset',type=Path)
    test=sub.add_parser('replay'); test.add_argument('--bundle',required=True,type=Path); test.add_argument('--dataset',type=Path); test.add_argument('--manifest-sha256',help='Independently recorded SHA256 of private-bundle.json')
    args=parser.parse_args()
    if args.action == 'build': build(args.destination,args.port,args.dataset)
    else: replay(args.bundle,dataset=args.dataset,expected_manifest_sha=args.manifest_sha256)


if __name__ == '__main__': fail_cli(main)
