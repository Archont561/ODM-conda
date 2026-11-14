"""Exercise the exact private ODM patch against small isolated stubs."""
import importlib.util
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Exact upstream source shape ensures the patch cannot silently stop applying.
UPSTREAM = '''import os
from opendm.ai import get_model
from opendm import log
from opendm.system import run
from opendm import io

def classify(point_cloud, max_threads=8):
    tmp_output = io.related_file_path(point_cloud, postfix=".classified")
    if os.path.isfile(tmp_output):
        os.remove(tmp_output)

    try:
        model = get_model("openpointclass", 
            "https://github.com/uav4geo/OpenPointClass/releases/download/v1.1.3/vehicles-vegetation-buildings.zip", 
            "v1.0.0",
            name="model.bin")

        if model is not None:
            run('pcclassify "%s" "%s" "%s" -u -s 2,64' % (point_cloud, tmp_output, model), env_vars={'OMP_NUM_THREADS': max_threads})
            
            if os.path.isfile(tmp_output):
                os.remove(point_cloud)
                os.rename(tmp_output, point_cloud)
            else:
                log.ODM_WARNING("Cannot classify using OpenPointClass (no output generated)")
        else:
            log.ODM_WARNING("Cannot download/access model from %s" % (model_url))

    except Exception as e:
        log.ODM_WARNING("Cannot classify using OpenPointClass: %s" % str(e))

'''


@pytest.fixture
def opc(tmp_path, monkeypatch):
    (tmp_path/'opendm').mkdir()
    path = tmp_path/'opendm/opc.py'; path.write_text(UPSTREAM)
    subprocess.run(['patch', '-p1', '-i', str(ROOT/'research/recipes/odm-dense-research/patches/0003-classification-fail-closed.patch')], cwd=tmp_path, check=True, capture_output=True)
    package = types.ModuleType('opendm'); package.__path__ = []
    ai = types.ModuleType('opendm.ai'); ai.get_model = lambda *a, **k: '/private/model'
    system = types.ModuleType('opendm.system'); system.run = lambda *a, **k: None
    package.log = types.SimpleNamespace(ODM_WARNING=lambda *a: None)
    package.io = types.SimpleNamespace(related_file_path=lambda path, postfix: str(path)+postfix)
    for name, module in [('opendm', package), ('opendm.ai', ai), ('opendm.system', system)]:
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setenv('ODM_CONDA_MODEL_ROOT', '/private/models')
    spec = importlib.util.spec_from_file_location('tested_opc', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_classifier_error_preserves_input(opc, tmp_path):
    cloud = tmp_path/'cloud.laz'; cloud.write_bytes(b'original')
    def fail(*args, **kwargs):
        raise RuntimeError('classifier failed')
    opc.run = fail
    with pytest.raises(RuntimeError, match='classifier failed'):
        opc.classify(str(cloud))
    assert cloud.read_bytes() == b'original'


@pytest.mark.parametrize('output', [None, b''])
def test_missing_or_empty_output_preserves_input(opc, tmp_path, output):
    cloud = tmp_path/'cloud.laz'; cloud.write_bytes(b'original')
    if output is not None:
        opc.run = lambda *a, **k: Path(str(cloud)+'.classified').write_bytes(output)
    with pytest.raises(RuntimeError, match='no nonempty output'):
        opc.classify(str(cloud))
    assert cloud.read_bytes() == b'original'


def test_success_replaces_input(opc, tmp_path):
    cloud = tmp_path/'cloud.laz'; cloud.write_bytes(b'original')
    opc.run = lambda *a, **k: Path(str(cloud)+'.classified').write_bytes(b'classified')
    opc.classify(str(cloud))
    assert cloud.read_bytes() == b'classified'


def test_missing_model_fails(opc, tmp_path):
    cloud = tmp_path/'cloud.laz'; cloud.write_bytes(b'original')
    opc.get_model = lambda *a, **k: None
    with pytest.raises(RuntimeError, match='model'):
        opc.classify(str(cloud))
    assert cloud.read_bytes() == b'original'


def test_hosted_evidence():
    import json
    evidence = json.loads((ROOT/'research/odm-classification-failure-integration-evidence.json').read_text())
    assert evidence['classification_stats']['count'] == 41276
    assert evidence['classification_stats']['maximum'] == 6
    assert evidence['no_binary_overlay'] and evidence['relocated_locked_replay']
    assert 'fault injection' in evidence['checks']
    assert 'discarded' in evidence['retention']
