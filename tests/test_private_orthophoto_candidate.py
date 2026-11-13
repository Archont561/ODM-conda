import json
from pathlib import Path
import pytest
from common import ScaffoldError, sha256
import private_orthophoto_candidate as candidate


def test_private_candidate_retains_same_staged_package_and_source(tmp_path, monkeypatch):
    def prepare(stage):
        (stage/'recipes/odm-orthophoto').mkdir(parents=True)
        (stage/'recipes/odm-orthophoto/recipe.yaml').write_text('candidate recipe')
        (stage/'recipes/components.json').write_text('{}')
    def source(name, component, destination, cache, root):
        assert (root/'recipes/odm-orthophoto/recipe.yaml').read_text() == 'candidate recipe'
        destination.mkdir(); path=destination/'source.tar.gz'; path.write_bytes(b'source'); return path
    def build(recipe, name, work):
        path=work/'output/linux-64/odm-orthophoto-x-candidate_opencv413_hash_3.conda'
        path.parent.mkdir(parents=True); path.write_bytes(b'binary'); return path
    def audit(args):
        output=Path(args[args.index('--output-dir')+1]); report=Path(args[args.index('--reports-dir')+1]); report.mkdir()
        package=next(output.glob('linux-64/*.conda'))
        (report/'audit-odm-orthophoto.json').write_text(json.dumps({'sha256':sha256(package),'result':'passed'}))
    monkeypatch.setattr(candidate, 'prepare', prepare)
    monkeypatch.setattr(candidate, 'config', lambda root: {'components': {'odm-orthophoto': {}}})
    monkeypatch.setattr(candidate, 'make_bundle', source)
    monkeypatch.setattr(candidate, 'build_recipe', build)
    monkeypatch.setattr(candidate, 'run', audit)
    dest=tmp_path/'private'; candidate.create(dest)
    receipt=json.loads((dest/'receipt.json').read_text())
    assert sha256(dest/'package'/receipt['package']['filename']) == receipt['package']['sha256']
    assert sha256(dest/'source'/receipt['source_bundle']['filename']) == receipt['source_bundle']['sha256']
    assert dest.stat().st_mode & 0o077 == 0
    with pytest.raises(ScaffoldError): candidate.create(dest)


def test_failed_build_removes_private_output(tmp_path, monkeypatch):
    monkeypatch.setattr(candidate, 'prepare', lambda _: (_ for _ in ()).throw(ValueError('failed')))
    dest=tmp_path/'private'
    with pytest.raises(ValueError): candidate.create(dest)
    assert not dest.exists()


def test_handoff_evidence_has_distinct_scoped_identity():
    from common import ROOT
    data=json.loads((ROOT/'research/odm-orthophoto-handoff-integration.json').read_text())
    orth=[p for p in data['local_packages'] if p['filename'].startswith('odm-orthophoto-')]
    assert len(orth)==1 and '-candidate_opencv413_' in orth[0]['filename']
    assert len(orth[0]['sha256'])==64 and len(data['source_bundle']['sha256'])==64
    assert data['source_manifest_entries']==444 and data['inventory_package_count']==432
    assert 'not full dependency closure' in data['scope']
