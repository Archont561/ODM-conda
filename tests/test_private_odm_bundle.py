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
