"""The fast-orthophoto GDAL consumers must target the same ABI as PDAL."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_fast_path_gdal_recipes_build_and_run_against_same_abi():
    for name in ('dem2points', 'fastrasterfilter', 'odm-orthophoto'):
        recipe = yaml.safe_load((ROOT / 'recipes' / name / 'recipe.yaml').read_text())
        for scope in ('host', 'run'):
            assert 'libgdal-core >=3.12.2,<3.12.3' in recipe['requirements'][scope], (name, scope)
        assert recipe['build']['number'] >= 1, name
        component = json.loads((ROOT / 'recipes/components.json').read_text())['components'][name]
        assert component['build_number'] == recipe['build']['number']


def test_renderdem_builds_against_the_compatible_pdal_and_gdal():
    recipe = yaml.safe_load((ROOT / "recipes/renderdem/recipe.yaml").read_text())
    for scope in ("host", "run"):
        assert "libpdal-core >=2.10.0,<2.10.1" in recipe["requirements"][scope]
        assert "libgdal-core >=3.12.2,<3.12.3" in recipe["requirements"][scope]
