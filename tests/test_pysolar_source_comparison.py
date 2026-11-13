import json
from pathlib import Path


def test_bounded_pysolar_source_comparison():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/pysolar-source-comparison.json').read_text())
    assert data['sdist']['sha256']=='05913740694e4bb2af8412de3fa278c0435b3b15b2975c8e38625fc4eed1fd6c'
    assert data['github_commit']=='42a1c3311ac3df1fb906abb9723df12804a73426'
    assert data['shared_files']==26 and data['different_shared_files']==0
    assert data['shared_files']+data['sdist_only_files']==data['sdist']['files']
    assert data['shared_files']+data['github_only_files']==data['github_files']
    assert 'not rights' in data['scope']
