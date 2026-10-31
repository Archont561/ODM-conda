from pathlib import Path
import pytest
from common import ScaffoldError
import prepare_opencv413_research as experiment


def test_experiment_copies_only_expected_constraints_and_does_not_mutate_source(tmp_path, monkeypatch):
    root = tmp_path/'repo'; root.mkdir()
    files = []
    for name in experiment.RECIPES:
        file = root/name; file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(('build:\n  number: 2\n' if name == experiment.RECIPES[0] else '') + 'host: >=4.12,<4.13\nrun: >=4.12,<4.13\n')
        files.append(file)
    monkeypatch.setattr(experiment, 'repository_files', lambda _: files)
    destination = tmp_path/'stage'
    experiment.prepare(destination, root)
    for name in experiment.RECIPES:
        assert (root/name).read_text().count(experiment.OLD) == 2
        text = (destination/name).read_text()
        assert text.startswith(experiment.WARNING) and text.count(experiment.NEW) == 2
    assert 'string: research_${{ hash }}_2' in (destination/experiment.RECIPES[0]).read_text()
    with pytest.raises(ScaffoldError): experiment.prepare(destination, root)
    with pytest.raises(ScaffoldError): experiment.prepare(root/'inside', root)
    files[0].write_text('changed')
    with pytest.raises(ScaffoldError): experiment.prepare(tmp_path/'invalid', root)
    assert not (tmp_path/'invalid').exists()
