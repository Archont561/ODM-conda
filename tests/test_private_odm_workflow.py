"""The dispatch wrapper stays ephemeral and fails closed on dataset mismatch."""
import pytest

import run_private_odm_workflow as workflow
from common import ScaffoldError


def test_workflow_runs_pinned_dataset_and_discards_bundle(tmp_path, monkeypatch):
    monkeypatch.delenv('ODM_OPENMVS_VARIANT', raising=False)
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
    monkeypatch.delenv('ODM_OPENMVS_VARIANT', raising=False)
    summary = tmp_path / 'summary'
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    monkeypatch.setattr(workflow, 'run', lambda cmd: None)
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: 'wrong')
    monkeypatch.setattr(workflow, 'build', lambda *a: pytest.fail('build must not run'))
    with pytest.raises(ScaffoldError, match='dataset commit'):
        workflow.main()
    assert not summary.exists()


def test_tetraflow_selection_uses_reduced_scoped_build(tmp_path, monkeypatch):
    captured = []
    monkeypatch.setenv('ODM_OPENMVS_VARIANT', 'tetraflow')
    monkeypatch.setattr(workflow, 'run', lambda cmd: None)
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: workflow.DATASET_COMMIT)
    monkeypatch.setattr(workflow, 'download_crate', lambda path: path.write_bytes(b'crate'))
    monkeypatch.setattr(workflow, 'build', lambda *args, **kwargs: captured.append((args, kwargs)))
    workflow.main()
    args, kwargs = captured[0]
    assert kwargs['openmvs_variant'] == 'tetraflow'
    assert kwargs['runtime_profile'] == 'reduced' and kwargs['reduced_jxl'] is True
    assert kwargs['vendor_scope_crate'].name == 'jpegxl-src-0.11.2.crate'
    assert args[0].parent == kwargs['vendor_scope_crate'].parent
    assert not args[0].parent.exists()


def test_variant_rejected_before_any_build(monkeypatch):
    monkeypatch.setenv('ODM_OPENMVS_VARIANT', '$(touch /tmp/unsafe)')
    monkeypatch.setattr(workflow, 'run', lambda *a: pytest.fail('should not run'))
    with pytest.raises(ScaffoldError, match='Unknown OpenMVS'):
        workflow.main()


def test_crate_download_checks_hash_and_redirect(tmp_path, monkeypatch):
    import hashlib
    import io
    import prepare_jxl_vendor_scope
    class Response(io.BytesIO):
        url = workflow.CRATE_URL
    monkeypatch.setattr(prepare_jxl_vendor_scope, 'CRATE_SHA256', hashlib.sha256(b'crate').hexdigest())
    monkeypatch.setattr(workflow.urllib.request, 'urlopen', lambda *a, **k: Response(b'crate'))
    workflow.download_crate(tmp_path/'crate')
    assert (tmp_path/'crate').read_bytes() == b'crate'
    with pytest.raises(ScaffoldError, match='checksum'):
        monkeypatch.setattr(prepare_jxl_vendor_scope, 'CRATE_SHA256', '0'*64)
        workflow.download_crate(tmp_path/'bad')
    Response.url = 'https://example.com/unsafe'
    with pytest.raises(ScaffoldError, match='redirect'):
        workflow.download_crate(tmp_path/'redirect')
