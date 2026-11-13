import json
from pathlib import Path

import pytest
import yaml

from map_odm_python_requirements import compare

ROOT = Path(__file__).resolve().parents[1]


def test_recorded_map_matches_source_and_research_recipe():
    inventory = json.loads((ROOT/'research/odm-full-scope-source-inventory.json').read_text())
    recipe = yaml.safe_load((ROOT/'research/recipes/odm-fast-research/recipe.yaml').read_text())
    recorded = json.loads((ROOT/'research/odm-python-requirement-map.json').read_text())
    assert recorded == compare(inventory, recipe)
    names = {item['upstream_name'].lower(): item for item in recorded['requirements']}
    assert names['rawpy']['status'] == 'not-declared-directly'
    assert names['pillow-jxl-plugin']['candidate_name'] == 'odm-research-pillow-jxl-plugin'
    assert names['pyodm']['status'] == 'declared-directly'
    assert len(names) == len(inventory['requirements'])


def test_duplicate_or_invalid_run_spec_rejected():
    inv = {'source_commit': 'test', 'requirements': []}
    for run in (['Foo', 'foo'], ['!invalid']):
        with pytest.raises(ValueError):
            compare(inv, {'requirements': {'run': run}})
