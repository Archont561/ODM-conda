import pytest
from common import ScaffoldError
from classify_openmvs_notice_gaps import classify


def test_classifies_lmfit_and_rejects_unknown_or_missing_trace():
    comparison = {'package_sha256': 'hash', 'unmatched': ['libs/Math/LMFit/COPYING']}
    trace = {'entries': [{'path': 'libs/Math/LMFit/lmmin.cpp'}, {'path': 'libs/Math/LMFit/lmmin.h'}]}
    result = classify(comparison, trace)
    assert result['findings'][0]['trace_path_count'] == 2
    with pytest.raises(ScaffoldError, match='LMFit'):
        classify(comparison, {'entries': []})
    with pytest.raises(ScaffoldError, match='Unclassified'):
        classify({'package_sha256':'hash', 'unmatched':['new']}, trace)
