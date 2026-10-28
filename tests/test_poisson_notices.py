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
