from pathlib import Path
from common import ROOT


def test_reduced_recipe_differs_only_in_builder():
    full = (ROOT/'research/recipes/openmvs-odm/recipe.yaml').read_text()
    reduced = (ROOT/'research/recipes/openmvs-odm/reduced.yaml').read_text()
    assert reduced == '# Local-only reduced-tree build; no release approval.\n' + full.replace('../../../scripts/build_open_research.py', '../../../scripts/build_openmvs_reduced.py')


def test_runner_uses_reduced_recipe_and_individual_audits(monkeypatch, tmp_path):
    import run_reduced_research as runner
    calls = []
    monkeypatch.setattr(runner, 'run_one', lambda name, root: calls.append((name, root)))
    runner.run_all(tmp_path)
    assert [x[0] for x in calls] == ['poisson', 'opensfm', 'openmvs']
    assert len({p for _,p in calls}) == 3


def test_reduced_selection_routes_through_disposable_runner(monkeypatch, capsys):
    import run_reduced_research as reduced
    import run_open_research as research
    from record_open_research_component import record_component
    calls = []
    monkeypatch.setattr(reduced, 'run_one', lambda component, root: calls.append((component, root)))
    monkeypatch.setenv('RESEARCH_COMPONENT', 'reduced-opensfm')
    research.main()
    assert calls[0][0] == 'opensfm'
    assert not calls[0][1].exists()
    record_component('reduced-all')
    assert 'reduced-all' in capsys.readouterr().out
