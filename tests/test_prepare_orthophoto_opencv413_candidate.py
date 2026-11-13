import json
from pathlib import Path
import pytest
from common import ROOT, ScaffoldError
from prepare_orthophoto_opencv413_candidate import prepare


def test_candidate_stages_distinct_identity_and_closed_gates(tmp_path):
    dest = tmp_path / 'stage'
    original_recipe = (ROOT / 'recipes/odm-orthophoto/recipe.yaml').read_bytes()
    original_manifest = (ROOT / 'recipes/components.json').read_bytes()
    prepare(dest)
    text = (dest / 'recipes/odm-orthophoto/recipe.yaml').read_text()
    assert text.count('>=4.13,<4.14') == 2
    assert 'number: 3\n  string: candidate_opencv413_${{ hash }}_3' in text
    component = json.loads((dest / 'recipes/components.json').read_text())['components']['odm-orthophoto']
    assert component['build_number'] == 3
    assert component['release_checks'] and not any(component['release_checks'].values())
    assert (ROOT / 'recipes/odm-orthophoto/recipe.yaml').read_bytes() == original_recipe
    assert (ROOT / 'recipes/components.json').read_bytes() == original_manifest
    with pytest.raises(ScaffoldError):
        prepare(dest)
    with pytest.raises(ScaffoldError):
        prepare(ROOT / 'candidate-unsafe')


def test_recorded_hosted_candidate_has_correct_scope_and_abi():
    data = json.loads((ROOT / 'research/odm-orthophoto-opencv413-candidate-evidence.json').read_text())
    assert data['artifact'].endswith('-candidate_opencv413_873e7db_3.conda')
    assert data['sha256'] == data['audit']['sha256']
    assert data['audit']['result'] == 'passed'
    assert 'libopencv >=4.13,<4.14' in data['depends']
    assert 'libopencv_core.so.413' in data['audit']['elf_needed']
    assert 'unpublished' in data['scope']
