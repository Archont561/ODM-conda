"""The fast-orthophoto GDAL consumers must target the same ABI as PDAL."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_fast_path_gdal_recipes_build_and_run_against_same_abi():
    for name in ('dem2points', 'fastrasterfilter', 'odm-orthophoto'):
        recipe = yaml.safe_load((ROOT / 'recipes' / name / 'recipe.yaml').read_text())
        for scope in ('host', 'run'):
            assert 'libgdal-core >=3.12,<3.13' in recipe['requirements'][scope], (name, scope)
        assert recipe['build']['number'] >= 1, name
        component = json.loads((ROOT / 'recipes/components.json').read_text())['components'][name]
        assert component['build_number'] == recipe['build']['number']
