import json
from pathlib import Path


def test_bounded_codem_source_comparison():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/codem-source-comparison.json').read_text())
    assert data['sdist']['sha256'] == 'e5e0f31c0da46f6087ad38e988d0c4351282d67c05f325f96c63a24f76c8dec6'
    assert data['github_commit'] == '2264bc062ad827ca0f4558b3d0fb5ad40a90dcb3'
    assert data['shared_files'] == 25 and data['different_shared_files'] == 0
    assert data['shared_files'] + data['sdist_only_files'] == data['sdist']['files']
    assert data['shared_files'] + data['github_only_files'] == data['github_files']
    assert 'not rights' in data['scope']
