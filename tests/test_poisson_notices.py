"""Provisional PoissonRecon packages retain identified upstream notice variants."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_identified_poisson_notice_sources_are_packaged():
    component = json.loads((ROOT / 'recipes/components.json').read_text())['components']['poissonrecon-odm']
    notices = {item['source']: (item['target'], item['kind']) for item in component['notices']}
    for source in ('Src/Ply.h', 'Src/Ply.inl', 'Src/Array.h', 'Src/FEMTree.Initialize.inl',
                   'Src/BMPStream.inl', 'Src/SurfaceTrimmer.cpp', 'Src/MAT.h',
                   'Src/MyMiscellany.h', 'Src/PreProcessor.h', 'Src/RegularGrid.h'):
        assert notices[source][1] == 'first-comment'
    recipe = (ROOT / component['recipe']).read_text()
    for target, _ in notices.values():
        assert f'.conda-notices/{target}' in recipe
    assert not any(component['release_checks'].values())


def test_poisson_recipe_supplies_unaltered_ijg_notice():
    """The source patch and packaged notice preserve the identified 6b README."""
    import hashlib
    import subprocess
    import tempfile

    component = json.loads((ROOT / 'recipes/components.json').read_text())['components']['poissonrecon-odm']
    notice = next(n for n in component['notices'] if n['source'] == 'JPEG/README')
    assert notice == {'source': 'JPEG/README', 'target': 'IJG-6b-README.txt', 'kind': 'verbatim'}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / 'JPEG').mkdir()
        subprocess.run(['patch', '-p1', '--batch', '--fuzz=0', '-i',
                        str(ROOT / 'recipes/poissonrecon-odm/patches/0002-ijg-readme.patch')],
                       cwd=path, check=True, capture_output=True)
        restored = (path / 'JPEG/README').read_bytes()
        assert restored == (ROOT / 'research/notices/ijg-6b-README.txt').read_bytes()
        assert hashlib.sha256(restored).hexdigest() == (
            '4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478')
    assert 'IJG-6b-README.txt' in (ROOT / component['recipe']).read_text()
    assert not any(component['release_checks'].values())


def test_artifact_audit_rejects_a_modified_ijg_notice(tmp_path, monkeypatch):
    import pytest
    import audit_package
    from common import ScaffoldError

    component = json.loads((ROOT / 'recipes/components.json').read_text())['components']['poissonrecon-odm']
    name = 'poissonrecon-odm'
    artifact = tmp_path / f'{name}-{component["version"]}-build.conda'
    prefix = f'share/odm-conda/{name}'
    index = {'name': name, 'version': component['version'], 'build_number': component['build_number'],
             'build': 'build', 'subdir': 'linux-64',
             'depends': ['__glibc', 'libgcc', 'libstdcxx', 'libpng', 'libjpeg-turbo', 'libzlib', 'libgomp']}
    info = {'info/index.json': json.dumps(index).encode(),
            'info/about.json': json.dumps({'license': component['license']}).encode()}
    for i in range(len(component['notices']) + 1):
        info[f'info/licenses/{i}'] = b'notice'
    payload = {f'bin/{component["executable"]}': b'\x7fELF',
               f'{prefix}/SOURCE.txt': audit_package.source_url(name, component).encode(),
               f'{prefix}/upstream.json': json.dumps({'source': component['source']}).encode(),
               f'{prefix}/functional_test.py': b'', f'{prefix}/link-evidence.json': b'{}',
               f'share/licenses/{name}/packaging-MIT.txt': b''}
    for notice in component['notices']:
        payload[f'share/licenses/{name}/{notice["target"]}'] = b'bad'
    monkeypatch.setattr(audit_package, 'read_package', lambda _: (info, payload))
    with pytest.raises(ScaffoldError, match='IJG'):
        audit_package.audit(name, component, artifact)
