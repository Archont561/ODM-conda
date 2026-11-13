import json
from pathlib import Path


def test_bounded_pyodm_source_comparison():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/pyodm-source-comparison.json').read_text())
    assert data['sdist']['sha256']=='d0433182ac6d5587786391c91d0eeafe0d78c71d618336af78964620dafe87c4'
    assert data['github_commit']=='65ff9d0eafeef3b7cdedd4bd7915b43f53882219'
    assert data['shared_files']==8 and data['different_shared_files']==0
    assert data['shared_files']+data['sdist_only_files']==data['sdist']['files']
    assert data['shared_files']+data['github_only_files']==data['github_files']
    assert 'not rights' in data['scope']
