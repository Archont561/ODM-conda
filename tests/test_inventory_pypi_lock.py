import pytest
from common import ScaffoldError
from inventory_pypi_lock import summarize


def test_selected_packages_are_sanitized_and_unselected_ignored():
    url = 'https://user:secret@files.pythonhosted.org/packages/a/pkg.whl?token=secret'
    lock = {'environments': {'default': {'packages': {'linux-64': [{'pypi': url}]}}},
            'packages': [{'pypi': url, 'name': 'pkg', 'version': '1.0', 'hash': {'sha256': 'abc123'}},
                         {'pypi': 'https://files.pythonhosted.org/other.whl', 'name': 'other'}]}
    report = summarize(lock)
    assert report['packages'] == [{'binary_url': 'https://files.pythonhosted.org/packages/a/pkg.whl', 'name': 'pkg', 'version': '1.0', 'hash': {'sha256': 'abc123'}}]
    lock['packages'][0]['name'] = '/home/user/secret'
    with pytest.raises(ScaffoldError): summarize(lock)


def test_missing_and_untrusted_locations_fail_closed():
    lock = {'environments': {'default': {'packages': {'linux-64': [{'pypi': 'https://private.example/a'}]}}}, 'packages': []}
    with pytest.raises(ScaffoldError): summarize(lock)
    lock['packages'] = [{'pypi': 'https://private.example/a'}]
    with pytest.raises(ScaffoldError): summarize(lock)
