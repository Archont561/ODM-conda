import json

import pytest
import yaml

import conda_build_provenance as mod
from common import ScaffoldError


def record(name='libjxl'):
    return {'name': name, 'version': '0.11.2', 'build': 'h1_1', 'subdir': 'linux-64',
            'fn': f'{name}-0.11.2-h1_1.conda', 'sha256': 'a'*64,
            'license': 'BSD-3-Clause', 'url': f'https://example.org/linux-64/{name}-0.11.2-h1_1.conda?secret=token'}


def test_record_sanitizes_url_and_requires_complete_identity():
    result = mod.package_record(record())
    assert result['binary_package_url'] == 'https://example.org/linux-64/libjxl-0.11.2-h1_1.conda'
    for bad in (record() | {'sha256':'bad'}, record() | {'subdir':'win-64'},
                record() | {'fn':'../bad.conda'}, record() | {'url':'http://example.org/bad.conda'},
                record() | {'url':'https://user:secret@example.org/linux-64/libjxl-0.11.2-h1_1.conda'}):
        with pytest.raises(ScaffoldError): mod.package_record(bad)


def test_inspect_reports_sorted_groups_and_rejects_missing_or_duplicates(tmp_path, monkeypatch):
    file = tmp_path/'package.conda'; file.write_bytes(b'dummy')
    index = {'name':'example', 'version':'1', 'build':'research_1', 'subdir':'linux-64'}
    rendered = {'finalized_dependencies': {'build': {'resolved':[record('z'), record('a')]},
                                           'host': {'resolved':[record()]}}}
    def info(value):
        return {'info/index.json':json.dumps(index).encode(), 'info/recipe/rendered_recipe.yaml':yaml.safe_dump(value).encode()}, {}
    monkeypatch.setattr(mod, 'read_package', lambda _: info(rendered))
    result = mod.inspect(file)
    assert [r['name'] for r in result['build']] == ['a','z']
    assert result['host'][0]['name'] == 'libjxl'
    assert result['output']['sha256'] == mod.sha256(file)
    rendered['finalized_dependencies']['host']['resolved'] = [record(), record()]
    with pytest.raises(ScaffoldError, match='duplicate'): mod.inspect(file)
    del rendered['finalized_dependencies']['build']
    with pytest.raises(ScaffoldError, match='resolved build'): mod.inspect(file)
