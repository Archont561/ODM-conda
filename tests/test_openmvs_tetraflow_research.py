import hashlib

import pytest

from common import ScaffoldError


def test_alternative_source_requires_hashes_absence_and_specific_patch(tmp_path, monkeypatch):
    import build_openmvs_tetraflow_research as mod
    contents = {
        'libs/CMakeLists.txt': b'original libs',
        'apps/CMakeLists.txt': b'original apps',
        'libs/Math/TetraFlow.h': b'new solver',
        'libs/MVS/SceneReconstruct.cpp': b'typedef SEACAVE::TetraFlow maxflow_t;',
        'libs/MVS/CMakeLists.txt': b'LIST(REMOVE_ITEM LIBRARY_FILES_C "${PATH_PythonWrapper_cpp}")\n',
    }
    for name,value in contents.items():
        file=tmp_path/name; file.parent.mkdir(parents=True,exist_ok=True); file.write_bytes(value)
    monkeypatch.setattr(mod,'PINNED',{name:hashlib.sha256(value).hexdigest() for name,value in contents.items()})
    mod.prepare_source(tmp_path)
    assert 'SceneDensify.cpp' in (tmp_path/'libs/MVS/CMakeLists.txt').read_text()
    with pytest.raises(ScaffoldError,match='Unexpected alternative source'):
        mod.prepare_source(tmp_path)


def test_alternative_source_rejects_named_restricted_directories(tmp_path,monkeypatch):
    import build_openmvs_tetraflow_research as mod
    monkeypatch.setattr(mod,'PINNED',{})
    (tmp_path/'libs/Math/IBFS').mkdir(parents=True)
    with pytest.raises(ScaffoldError,match='Restricted directory present'):
        mod.prepare_source(tmp_path)


def test_jxl_abi_is_constrained_for_build_and_runtime():
    import yaml
    from common import ROOT

    recipe = yaml.safe_load((ROOT / 'research/recipes/openmvs-tetraflow-research/recipe.yaml').read_text())
    for environment in ('host', 'run'):
        assert 'libjxl >=0.11,<0.12' in recipe['requirements'][environment]
    assert any('ldd' in item.get('script', {}).get('content', '') for item in recipe['tests'])
