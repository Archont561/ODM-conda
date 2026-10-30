"""Research artifacts must reject leaked sources even though they are never uploaded."""
import pytest

from common import ScaffoldError
from audit_open_research import verify_payload


def test_research_audit_rejects_unexpected_checkout_and_sources(monkeypatch):
    import audit_open_research as audit
    monkeypatch.setattr(audit, "OPENMVS_NOTICES", {})
    payload = {
        'bin/ReconstructMesh': b'\x7fELFbinary',
        'share/odm-conda/openmvs-odm/functional_test.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_synthetic_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_pointcloud_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/texrecon_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/SOURCE.txt': b'LOCAL RESEARCH ONLY',
        'share/licenses/openmvs-odm/packaging-MIT.txt': b'notice',
        'share/licenses/openmvs-odm/upstream-LICENSE.txt': b'notice',
    }
    verify_payload('openmvs-odm', payload)
    payload['share/odm-conda/openmvs-odm/.git/config'] = b'leaked'
    with pytest.raises(ScaffoldError, match='leak'):
        verify_payload('openmvs-odm', payload)


def test_research_package_identity_and_runtime_dependencies_fail_closed():
    from audit_open_research import verify_index

    index = {'name': 'opensfm-odm', 'version': '0.5.2', 'build_number': 5, 'subdir': 'linux-64',
             'depends': ['python >=3.12,<3.13', 'numpy', 'py-opencv >=4.12,<4.13',
                         'ceres-solver', 'suitesparse', 'gflags', 'glog', 'libgomp', 'rasterio', 'rawpy']}
    verify_index('opensfm-odm', index)
    for changed in ({**index, 'version': '9.9'}, {**index, 'build_number': 0},
                    {**index, 'depends': [d for d in index['depends'] if not d.startswith('numpy')]},
                    {**index, 'depends': 'python numpy'}, {**index, 'subdir': 'osx-arm64'}):
        with pytest.raises(ScaffoldError):
            verify_index('opensfm-odm', changed)


def test_scoped_asset_audit_rejects_missing_guard_and_reintroduced_assets(monkeypatch):
    import audit_open_research as audit
    import hashlib
    expected = b'guarded dataset'
    guard = b'guard code'
    monkeypatch.setattr(audit, 'SCOPED_DATASET_SHA256', hashlib.sha256(expected).hexdigest())
    monkeypatch.setattr(audit, 'SCOPED_GUARD_SHA256', hashlib.sha256(guard).hexdigest())
    root = 'lib/python3.12/site-packages/opensfm/'
    payload = {root + 'dataset.py': expected, root + 'scoped_runtime_guard.py': guard}
    audit.verify_scoped_assets(payload)
    for bad in ({root + 'dataset.py': expected},
                {**payload, root + 'data/sensor_data.sqlite': b'unwanted'},
                {**payload, root + 'data/bow/bow_hahog_root_uchar_64.npz': b'unwanted'},
                {**payload, root + 'data/bow/unknown.npz': b'unwanted'},
                {**payload, root + 'dataset.py': b'modified'}):
        with pytest.raises(ScaffoldError):
            audit.verify_scoped_assets(bad)


def test_scoped_index_requires_mutual_exclusion_constraint():
    from audit_open_research import verify_index
    index = {'name': 'opensfm-scoped-odm', 'version': '0.5.2', 'build_number': 0, 'subdir': 'linux-64',
             'depends': ['python', 'numpy', 'py-opencv', 'ceres-solver', 'suitesparse', 'gflags', 'glog', 'libgomp', 'rasterio', 'rawpy'],
             'constrains': ['opensfm-odm <0']}
    verify_index('opensfm-scoped-odm', index)
    with pytest.raises(ScaffoldError):
        verify_index('opensfm-scoped-odm', {**index, 'constrains': []})


def test_openmvs_conda_license_metadata_requires_exact_notices(monkeypatch):
    import hashlib
    import audit_open_research as audit
    upstream = b'upstream license'
    lmfit = b'lmfit license'
    monkeypatch.setattr(audit, 'OPENMVS_METADATA_NOTICES', {'LICENSE': hashlib.sha256(upstream).hexdigest(), 'COPYING': hashlib.sha256(lmfit).hexdigest()})
    info = {'info/licenses/LICENSE': upstream, 'info/licenses/libs/Math/LMFit/COPYING': lmfit}
    audit.verify_openmvs_metadata_notices(info)
    with pytest.raises(ScaffoldError, match='Missing or modified'):
        audit.verify_openmvs_metadata_notices({'info/licenses/LICENSE': upstream})
    with pytest.raises(ScaffoldError, match='Missing or modified'):
        audit.verify_openmvs_metadata_notices({**info, 'info/licenses/libs/Math/LMFit/COPYING': b'changed'})


def test_openmvs_recipe_and_payload_both_include_traced_lmfit_notice():
    import yaml
    from common import ROOT
    from research_license_notices import OPENMVS_NOTICES
    recipe = yaml.safe_load((ROOT / 'research/recipes/openmvs-odm/recipe.yaml').read_text())
    path, digest = OPENMVS_NOTICES['lmfit-COPYING.txt']
    assert path == 'libs/Math/LMFit/COPYING'
    assert digest == '09c21b5a8ca469b20e0ce3795f19370affba36f532e480e593c9712c91caf4c4'
    assert path in recipe['about']['license_file']
