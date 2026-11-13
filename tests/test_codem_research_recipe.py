from pathlib import Path
import yaml


def test_codem_research_recipe_checks_relocatable_commands_and_remains_unreviewed():
    root = Path(__file__).resolve().parents[1]
    recipe = yaml.safe_load((root/'research/recipes/python-source-research/codem.yaml').read_text())
    script = recipe['build']['script']['content']
    assert "for name in ('codem', 'vcd')" in script
    assert "os.fsencode(prefix / 'bin' / 'python')" in script
    files = recipe['tests'][0]['package_contents']['files']
    assert files == ['bin/codem', 'bin/vcd']
    assert "for name in ('codem', 'vcd')" in recipe['tests'][1]['script']['content']
    assert recipe['about']['license'] == 'LicenseRef-Unreviewed'
