"""Dem2mesh must preserve the vendored simplifier's MIT permission text."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recipe_patches_and_packages_identified_mit_notice(tmp_path):
    component = json.loads((ROOT / 'recipes/components.json').read_text())['components']['dem2mesh']
    notice = next(n for n in component['notices'] if n['source'] == 'Simplify-MIT.txt')
    assert notice == {'source': 'Simplify-MIT.txt', 'target': 'Simplify-upstream-MIT.txt', 'kind': 'verbatim'}
    patch = ROOT / 'recipes/dem2mesh/patches/0001-simplify-mit-notice.patch'
    subprocess.run(['patch', '-p1', '--batch', '--fuzz=0', '-i', str(patch)], cwd=tmp_path,
                   check=True, capture_output=True)
    content = (tmp_path / 'Simplify-MIT.txt').read_bytes()
    assert hashlib.sha256(content).hexdigest() == '0740ee1d8869b715e5d492ec4961a415a543f4a556d79b3a9ba6fda4d38c6fd0'
    assert content == (ROOT / 'research/notices/fast-quadric-2019-MIT.txt').read_bytes()
    assert '.conda-notices/Simplify-upstream-MIT.txt' in (ROOT / component['recipe']).read_text()
    assert not any(component['release_checks'].values())


def test_artifact_audit_rejects_a_modified_simplifier_notice(tmp_path, monkeypatch):
    import pytest
    import audit_package
    from common import ScaffoldError

    component = json.loads((ROOT / 'recipes/components.json').read_text())['components']['dem2mesh']
    name = 'dem2mesh'
    artifact = tmp_path / f'{name}-{component["version"]}-build.conda'
    prefix = f'share/odm-conda/{name}'
    index = {'name': name, 'version': component['version'], 'build_number': component['build_number'],
             'build': 'build', 'subdir': 'linux-64',
             'depends': ['__glibc', 'libgcc', 'libstdcxx', 'libgdal-core', 'libgomp']}
    info = {'info/index.json': json.dumps(index).encode(),
            'info/about.json': json.dumps({'license': component['license']}).encode()}
    for i in range(len(component['notices']) + 1):
        info[f'info/licenses/{i}'] = b'notice'
    payload = {f'bin/{component["executable"]}': b'\x7fELF',
               f'{prefix}/SOURCE.txt': audit_package.source_url(name, component).encode(),
               f'{prefix}/upstream.json': json.dumps({'source': component['source']}).encode(),
               f'{prefix}/functional_test.py': b'', f'share/licenses/{name}/packaging-MIT.txt': b''}
    for notice in component['notices']:
        payload[f'share/licenses/{name}/{notice["target"]}'] = b'bad'
    monkeypatch.setattr(audit_package, 'read_package', lambda _: (info, payload))
    with pytest.raises(ScaffoldError, match='Simplify'):
        audit_package.audit(name, component, artifact)
