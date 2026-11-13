"""Private bundle integrity must be checked before any replay."""
import pytest


def test_sealed_bundle_detects_mutation_and_unexpected_packages(tmp_path):
    from private_odm_bundle import seal, verify
    from common import ScaffoldError

    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True)
    (bundle/'channel/noarch').mkdir()
    (bundle/'pixi.toml').write_text('manifest')
    (bundle/'pixi.lock').write_text('lock')
    (bundle/'channel/linux-64/repodata.json').write_text('{}')
    (bundle/'channel/noarch/repodata.json').write_text('{}')
    package=bundle/'channel/linux-64/example.conda'; package.write_bytes(b'package')
    seal(bundle,48179)
    assert verify(bundle)==48179
    package.write_bytes(b'tampered')
    with pytest.raises(ScaffoldError,match='checksum'):
        verify(bundle)
    package.write_bytes(b'package')
    (bundle/'channel/linux-64/extra.conda').write_bytes(b'extra')
    with pytest.raises(ScaffoldError,match='unexpected'):
        verify(bundle)


def test_private_destination_must_be_outside_repo_and_new(tmp_path):
    from private_odm_bundle import validate_destination
    from common import ScaffoldError

    repo=tmp_path/'repo';repo.mkdir()
    with pytest.raises(ScaffoldError): validate_destination(repo/'secret',repo)
    existing=tmp_path/'existing';existing.mkdir()
    with pytest.raises(ScaffoldError): validate_destination(existing,repo)
    validate_destination(tmp_path/'new',repo)


def test_private_variant_identity_does_not_overwrite_production_recipe(tmp_path):
    from private_odm_bundle import private_identity
    from common import ScaffoldError
    recipe=tmp_path/'recipe.yaml'; recipe.write_text('build:\n  number: 2\n  skip: false\n')
    private_identity(recipe,2)
    assert 'string: research_${{ hash }}_2' in recipe.read_text()
    with pytest.raises(ScaffoldError): private_identity(recipe,1)


def test_verify_can_anchor_manifest_hash(tmp_path):
    import hashlib
    from private_odm_bundle import seal, verify
    from common import ScaffoldError
    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True); (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml','pixi.lock','channel/linux-64/repodata.json','channel/noarch/repodata.json','channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    seal(bundle,48179)
    digest=hashlib.sha256((bundle/'private-bundle.json').read_bytes()).hexdigest()
    assert verify(bundle,expected_manifest_sha=digest)==48179
    with pytest.raises(ScaffoldError,match='manifest checksum'):
        verify(bundle,expected_manifest_sha='0'*64)


def test_pinned_sdist_download_checks_content_and_url(tmp_path, monkeypatch):
    import hashlib
    import io
    from private_odm_bundle import download_sdist
    from common import ScaffoldError
    class Response(io.BytesIO):
        url = 'https://files.pythonhosted.org/source.tar.gz'
    monkeypatch.setattr('private_odm_bundle.urllib.request.urlopen',lambda *_args, **_kwargs: Response(b'source'))
    digest=hashlib.sha256(b'source').hexdigest()
    download_sdist(Response.url,digest,tmp_path/'source.tar.gz')
    assert (tmp_path/'source.tar.gz').read_bytes()==b'source'
    with pytest.raises(ScaffoldError, match='checksum mismatch'):
        download_sdist(Response.url,'0'*64,tmp_path/'bad.tar.gz')
    with pytest.raises(ScaffoldError, match='Unexpected pinned'):
        download_sdist('https://example.com/archive',digest,tmp_path/'bad-url.tar.gz')


def test_inventory_is_sealed_and_legacy_bundle_remains_supported(tmp_path):
    import json
    from private_odm_bundle import inventory_identities, seal, verify
    from common import ScaffoldError
    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True); (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml','pixi.lock','channel/linux-64/repodata.json','channel/noarch/repodata.json','channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    seal(bundle,48179)
    assert json.loads((bundle/'private-bundle.json').read_text())['schema_version']==1
    assert verify(bundle)==48179
    package={'name':'example','version':'1','build':'research_1','sha256':'a'*64,'binary_package_url':'http://127.0.0.1/linux-64/example.conda'}
    inv=bundle/'conda-inventory.json'; inv.write_text(json.dumps({'packages':[package]}))
    seal(bundle,48179)
    assert json.loads((bundle/'private-bundle.json').read_text())['schema_version']==2
    assert verify(bundle)==48179
    assert len(inventory_identities(json.loads(inv.read_text())))==1
    inv.write_text('{}')
    with pytest.raises(ScaffoldError,match='checksum'): verify(bundle)
    with pytest.raises(ScaffoldError,match='Invalid private Conda inventory'): inventory_identities({})
    with pytest.raises(ScaffoldError,match='Duplicate'): inventory_identities({'packages':[package,package]})


def test_replay_compares_retained_inventory_and_refuses_changed_records(tmp_path, monkeypatch):
    import json
    from contextlib import contextmanager
    import inventory_conda_environment
    import private_odm_bundle as bundle_script
    from common import ScaffoldError
    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True); (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml','pixi.lock','channel/linux-64/repodata.json','channel/noarch/repodata.json','channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    package={'name':'example','version':'1','build':'research_1','sha256':'a'*64,'binary_package_url':'http://127.0.0.1/linux-64/example.conda'}
    (bundle/'conda-inventory.json').write_text(json.dumps({'packages':[package]}))
    bundle_script.seal(bundle,48179)
    @contextmanager
    def loopback(_directory,_port):
        yield 'http://127.0.0.1:48179'
    monkeypatch.setattr(bundle_script,'loopback',loopback)
    monkeypatch.setattr(bundle_script,'run',lambda *_args,**_kwargs: None)
    monkeypatch.setattr(inventory_conda_environment,'inventory',lambda _prefix: {'packages':[package]})
    bundle_script.replay(bundle)
    monkeypatch.setattr(inventory_conda_environment,'inventory',lambda _prefix: {'packages':[package | {'build':'different'}]})
    with pytest.raises(ScaffoldError,match='inventory differs'):
        bundle_script.replay(bundle)


def test_reduced_profile_constraints_and_validation(tmp_path):
    from common import ScaffoldError
    from private_odm_bundle import configure_runtime_profile, validate_runtime_profile
    manifest = tmp_path/'pixi.toml'
    manifest.write_text('[workspace]\nname = "trial"\n[dependencies]\n')
    configure_runtime_profile(manifest, 'reduced')
    text = manifest.read_text()
    assert 'libspatialite = { version = "==5.1.0", build = "lgpl_*" }' in text
    assert 'libarchive = { version = "==3.8.11", build = "lgpl_*" }' in text
    records = {'packages': [
        {'name': 'libspatialite', 'version': '5.1.0', 'build': 'lgpl_x_19'},
        {'name': 'libarchive', 'version': '3.8.11', 'build': 'lgpl_x_0'},
    ]}
    validate_runtime_profile(records, 'reduced')
    for bad in (
        {'packages': records['packages'] + [{'name': 'lzo'}]},
        {'packages': records['packages'] + [{'name': 'librttopo'}]},
        {'packages': [records['packages'][0] | {'build': 'gpl_x'}, records['packages'][1]]},
        {'packages': [records['packages'][0], records['packages'][1] | {'version': '3.8.10'}]},
        {'packages': []},
    ):
        with pytest.raises(ScaffoldError):
            validate_runtime_profile(bad, 'reduced')
    with pytest.raises(ScaffoldError):
        configure_runtime_profile(manifest, 'unknown')
    malformed = tmp_path/'bad.toml'; malformed.write_text('[workspace]\n')
    with pytest.raises(ScaffoldError, match='manifest'):
        configure_runtime_profile(malformed, 'reduced')


def test_reduced_jxl_selects_distinct_odm_and_dependency_identities(tmp_path):
    from pathlib import Path
    from common import ScaffoldError
    from private_odm_bundle import configure_odm_research_recipe
    original = Path(__file__).resolve().parents[1]/'research/recipes/odm-fast-research/recipe.yaml'
    default=tmp_path/'default.yaml'; default.write_text(original.read_text())
    reduced=tmp_path/'reduced.yaml'; reduced.write_text(original.read_text())
    configure_odm_research_recipe(default)
    configure_odm_research_recipe(reduced, reduced_jxl=True)
    assert 'build:\n  number: 3\n' in default.read_text()
    assert 'odm-research-pillow-jxl-plugin ==1.3.4 research_*_1' in default.read_text()
    assert 'build:\n  number: 4\n' in reduced.read_text()
    assert 'odm-research-pillow-jxl-plugin ==1.3.4 research_reduced_*_2' in reduced.read_text()
    altered=tmp_path/'altered.yaml'; altered.write_text(original.read_text().replace('research_*_1', 'research_*_9'))
    with pytest.raises(ScaffoldError,match='JPEG XL'):
        configure_odm_research_recipe(altered, reduced_jxl=True)


def test_optional_jxl_replay_uses_the_installed_prefix(tmp_path, monkeypatch):
    from contextlib import contextmanager
    import private_odm_bundle as mod
    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True); (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml','pixi.lock','channel/linux-64/repodata.json','channel/noarch/repodata.json','channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    mod.seal(bundle,48179)
    @contextmanager
    def loopback(_directory,_port):
        yield 'http://127.0.0.1:48179'
    calls=[]
    monkeypatch.setattr(mod,'loopback',loopback)
    monkeypatch.setattr(mod,'run',lambda command,**kwargs: calls.append((command,kwargs)))
    monkeypatch.setenv('PYTHONPATH','/unexpected')
    mod.replay(bundle,test_jxl=True)
    jxl=[(command,kwargs) for command,kwargs in calls if command[-1].endswith('jxl_synthetic_fixture.py')]
    assert len(jxl)==1 and jxl[0][0][0].endswith('/.pixi/envs/default/bin/python')
    assert 'PYTHONPATH' not in jxl[0][1]['env']


def test_vendor_scope_pins_distinct_jxl_and_odm_identities(tmp_path):
    from pathlib import Path
    from common import ScaffoldError
    from private_odm_bundle import configure_odm_research_recipe
    original = Path(__file__).resolve().parents[1]/'research/recipes/odm-fast-research/recipe.yaml'
    recipe=tmp_path/'recipe.yaml'; recipe.write_text(original.read_text())
    with pytest.raises(ScaffoldError, match='requires'):
        configure_odm_research_recipe(recipe, vendor_scope=True)
    configure_odm_research_recipe(recipe, reduced_jxl=True, vendor_scope=True)
    assert 'build:\n  number: 5\n' in recipe.read_text()
    assert 'odm-research-pillow-jxl-plugin ==1.3.4 research_vendor_scope_*_3' in recipe.read_text()


def test_vendor_scope_requires_verified_crate_before_build(tmp_path):
    from common import ScaffoldError
    from private_odm_bundle import build, PORT
    bad=tmp_path/'bad.crate'; bad.write_bytes(b'not a crate')
    dest=tmp_path/'bundle'
    with pytest.raises(ScaffoldError, match='requires'):
        build(dest, PORT, None, vendor_scope_crate=bad)
    with pytest.raises(ScaffoldError, match='archive'):
        build(dest, PORT, None, reduced_jxl=True, vendor_scope_crate=bad)
    assert not dest.exists()


def test_tetraflow_variant_has_distinct_private_identity_and_exact_dependency(tmp_path):
    from pathlib import Path
    from common import ScaffoldError
    from private_odm_bundle import configure_odm_research_recipe
    source = Path(__file__).resolve().parents[1]/'research/recipes/odm-fast-research/recipe.yaml'
    recipe = tmp_path/'recipe.yaml'; recipe.write_text(source.read_text())
    configure_odm_research_recipe(recipe, reduced_jxl=True, vendor_scope=True, openmvs_variant='tetraflow')
    text = recipe.read_text()
    assert 'openmvs-tetraflow-research ==0.0.0.dev20260827 research_*_1' in text
    assert 'openmvs-odm ==0.0.0.dev20260516' not in text
    assert 'string: research_tetraflow_${{ hash }}_5' in text
    assert 'odm-research-pillow-jxl-plugin ==1.3.4 research_vendor_scope_*_3' in text
    malformed = tmp_path/'bad.yaml'; malformed.write_text(source.read_text().replace('openmvs-odm ==0.0.0.dev20260516', 'openmvs-odm ==0'))
    with pytest.raises(ScaffoldError, match='OpenMVS dependency'):
        configure_odm_research_recipe(malformed, openmvs_variant='tetraflow')
    with pytest.raises(ScaffoldError, match='variant'):
        configure_odm_research_recipe(malformed, openmvs_variant='unknown')


def test_tetraflow_replay_checks_linkage_and_rejects_missing_library(tmp_path, monkeypatch):
    import json
    from contextlib import contextmanager
    from types import SimpleNamespace
    import inventory_conda_environment
    import private_odm_bundle as mod
    from common import ScaffoldError

    bundle=tmp_path/'bundle'; (bundle/'channel/linux-64').mkdir(parents=True); (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml','pixi.lock','channel/linux-64/repodata.json','channel/noarch/repodata.json','channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    package={'name':'openmvs-tetraflow-research','version':'1','build':'research_1','sha256':'a'*64,'binary_package_url':'http://127.0.0.1/linux-64/example.conda'}
    (bundle/'conda-inventory.json').write_text(json.dumps({'packages':[package]}))
    mod.seal(bundle,48179)
    @contextmanager
    def loopback(_directory,_port):
        yield 'http://127.0.0.1:48179'
    monkeypatch.setattr(mod,'loopback',loopback)
    monkeypatch.setattr(mod,'run',lambda *_args,**_kwargs: None)
    monkeypatch.setattr(inventory_conda_environment,'inventory',lambda _prefix: {'packages':[package]})
    observed=[]
    monkeypatch.setattr(mod.subprocess,'run',lambda args,**kwargs: (observed.append(args) or SimpleNamespace(stdout='all resolved',stderr='')))
    mod.replay(bundle)
    assert len(observed)==1 and observed[0][0]=='ldd' and observed[0][1].endswith('/bin/ReconstructMesh')
    monkeypatch.setattr(mod.subprocess,'run',lambda *_args,**_kwargs: SimpleNamespace(stdout='libjxl.so => not found',stderr=''))
    with pytest.raises(ScaffoldError,match='Unresolved TetraFlow'):
        mod.replay(bundle)


def test_candidate_summary_requires_anchor_and_detects_tampering(tmp_path):
    import json
    from common import ScaffoldError, sha256
    from private_odm_bundle import candidate_summary, seal
    bundle = tmp_path/'bundle'
    (bundle/'channel/linux-64').mkdir(parents=True)
    (bundle/'channel/noarch').mkdir()
    for name in ('pixi.toml', 'pixi.lock', 'channel/linux-64/repodata.json',
                 'channel/noarch/repodata.json', 'channel/linux-64/example.conda'):
        (bundle/name).write_text(name)
    item = {'name':'example','version':'1','build':'research_1',
            'sha256':'a'*64,'binary_package_url':'http://127.0.0.1/linux-64/example.conda'}
    (bundle/'conda-inventory.json').write_text(json.dumps({'packages':[item]}))
    seal(bundle, 48179)
    anchor = sha256(bundle/'private-bundle.json')
    result = candidate_summary(bundle, anchor)
    assert result['inventory_package_count'] == 1
    assert result['local_packages'] == [{'filename':'example.conda',
                                        'sha256':sha256(bundle/'channel/linux-64/example.conda')}]
    assert str(bundle) not in json.dumps(result)
    with pytest.raises(ScaffoldError, match='independent manifest'):
        candidate_summary(bundle, None)
    with pytest.raises(ScaffoldError, match='manifest checksum'):
        candidate_summary(bundle, '0'*64)
    (bundle/'pixi.lock').write_text('tampered')
    with pytest.raises(ScaffoldError, match='checksum'):
        candidate_summary(bundle, anchor)


def test_odm_package_test_uses_private_channel_and_fails_closed(tmp_path, monkeypatch):
    import private_odm_bundle as mod
    from common import ScaffoldError
    channel = tmp_path/'channel'; (channel/'linux-64').mkdir(parents=True)
    package = channel/'linux-64/odm-fast-research-3.6.2-research_1.conda'
    package.write_bytes(b'candidate')
    calls = []
    monkeypatch.setattr(mod, 'rattler', lambda: 'rattler-build')
    monkeypatch.setattr(mod, 'run', lambda cmd: calls.append(cmd))
    mod.test_odm_package(channel, 'http://127.0.0.1:48179', tmp_path/'out')
    cmd = calls[0]
    assert cmd[:4] == ['rattler-build', 'test', '--package-file', str(package)]
    assert cmd[cmd.index('--channel')+1] == 'http://127.0.0.1:48179'
    assert '--channel-priority' in cmd and 'strict' in cmd
    package.unlink()
    with pytest.raises(ScaffoldError, match='exactly one'):
        mod.test_odm_package(channel, 'http://127.0.0.1:48179', tmp_path/'out')


def test_tetraflow_orthophoto_candidate_has_distinct_pinned_identity(tmp_path):
    from common import ROOT, ScaffoldError
    from private_odm_bundle import configure_odm_research_recipe
    recipe = tmp_path/'recipe.yaml'
    recipe.write_text((ROOT/'research/recipes/odm-fast-research/recipe.yaml').read_text())
    with pytest.raises(ScaffoldError):
        configure_odm_research_recipe(recipe, orthophoto_candidate=True)
    configure_odm_research_recipe(recipe, reduced_jxl=True, vendor_scope=True, openmvs_variant='tetraflow', orthophoto_candidate=True)
    text = recipe.read_text()
    assert 'odm-orthophoto ==0.0.0.dev20250225 candidate_opencv413_*_3' in text
    assert 'string: research_tetraflow_orthocandidate_${{ hash }}_5' in text


def test_recorded_orthophoto_tetraflow_trial_has_candidate_identity():
    from common import ROOT
    import json
    evidence = json.loads((ROOT/'research/odm-orthophoto-tetraflow-integration.json').read_text())
    matches = [p for p in evidence['local_packages'] if p['filename'].startswith('odm-orthophoto-')]
    assert len(matches) == 1 and '-candidate_opencv413_' in matches[0]['filename']
    assert len(matches[0]['sha256']) == 64
    assert 'not release' in evidence['scope']


def test_external_candidate_requires_explicit_anchor_and_mode(tmp_path):
    from private_odm_bundle import build
    from common import ScaffoldError
    with pytest.raises(ScaffoldError, match='requires package'):
        build(tmp_path/'bundle', 48179, None, openmvs_variant='tetraflow', orthophoto_package=tmp_path/'candidate.conda')
    assert not (tmp_path/'bundle').exists()


def test_external_candidate_validates_digest_before_archive_read(tmp_path):
    from private_odm_bundle import stage_orthophoto_candidate
    from common import ScaffoldError
    package = tmp_path/'candidate.conda'; package.write_bytes(b'not a package')
    with pytest.raises(ScaffoldError, match='digest'):
        stage_orthophoto_candidate(package, '0'*64, tmp_path/'work')
    assert not (tmp_path/'work').exists()
