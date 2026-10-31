"""The dispatch wrapper stays ephemeral and fails closed on dataset mismatch."""
import pytest

import run_private_odm_workflow as workflow
from common import ScaffoldError


def test_workflow_runs_pinned_dataset_and_discards_bundle(tmp_path, monkeypatch):
    commands = []
    built = []
    summary = tmp_path / 'summary'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    monkeypatch.setattr(workflow, 'run', lambda cmd: commands.append(cmd))
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: workflow.DATASET_COMMIT + '\n')
    monkeypatch.setattr(workflow, 'build', lambda bundle, port, dataset: built.append((bundle, port, dataset)))
    workflow.main()
    assert commands[1][-2:] == [workflow.DATASET_URL, workflow.DATASET_COMMIT]
    bundle, port, dataset = built[0]
    assert port == workflow.PORT and bundle.parent == dataset.parent
    assert not bundle.parent.exists()
    assert 'discarded' in summary.read_text()


def test_workflow_rejects_wrong_dataset_before_build(tmp_path, monkeypatch):
    summary = tmp_path / 'summary'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    monkeypatch.setattr(workflow, 'run', lambda cmd: None)
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: 'wrong')
    monkeypatch.setattr(workflow, 'build', lambda *a: pytest.fail('build must not run'))
    with pytest.raises(ScaffoldError, match='dataset commit'):
        workflow.main()
    assert not summary.exists()
