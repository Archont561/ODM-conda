import copy
from pathlib import Path
import subprocess

import pytest
import odm_research_merge as merge


def sample(count=2):
    return {'num_points': count, 'dimensions': ', '.join(sorted(merge.DIMENSIONS)),
            'bounds': {'minx': 300000., 'maxx': 300010., 'miny': 4545000., 'maxy': 4545010., 'minz': 200., 'maxz': 210.},
            'metadata': {'major_version': 1, 'minor_version': 4, 'dataformat_id': 7,
                         'scale_x': .001, 'scale_y': .001, 'scale_z': .001, 'spatialreference': 'fixture',
                         'global_encoding': 16, 'filesource_id': 0, 'project_id': merge.NIL_UUID,
                         'system_id': 'PDAL', 'software_id': 'PDAL 2.10',
                         'vlr_0': {'user_id': 'LASF_Projection', 'record_id': 2112}}}


@pytest.fixture
def trial(tmp_path, monkeypatch):
    prefix = tmp_path/'prefix'; (prefix/'bin').mkdir(parents=True)
    pdal = prefix/'bin/pdal'; pdal.write_text('#!/bin/sh\n'); pdal.chmod(0o755)
    monkeypatch.setenv('ODM_CONDA_LOCAL_PREFIX', str(prefix))
    a = tmp_path/'a.laz'; b = tmp_path/'b.laz'; output = tmp_path/'out.laz'
    a.write_bytes(b'a'); b.write_bytes(b'b')
    monkeypatch.setattr(merge, '_same_crs', lambda wkts: len(set(wkts)) == 1)
    monkeypatch.setattr(merge, '_summary', lambda pdal, path, env: sample(4 if Path(path).name.startswith('.odm-merge-') else 2))
    def run(cmd, **kwargs):
        Path(cmd[4]).write_bytes(b'new valid cloud')
    monkeypatch.setattr(merge.subprocess, 'run', run)
    return a, b, output


def test_success_and_safe_replacement(trial):
    a, b, output = trial
    output.write_bytes(b'original')
    with pytest.raises(ValueError, match='already exists'):
        merge.merge([a, b], output)
    assert output.read_bytes() == b'original'
    merge.merge([a, b], output, rerun=True)
    assert output.read_bytes() == b'new valid cloud'


def test_child_failure_preserves_previous_and_cleans_temp(trial, monkeypatch):
    a, b, output = trial; output.write_bytes(b'original')
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ['pdal'])
    monkeypatch.setattr(merge.subprocess, 'run', fail)
    with pytest.raises(subprocess.CalledProcessError):
        merge.merge([a, b], output, rerun=True)
    assert output.read_bytes() == b'original'
    assert not list(output.parent.glob('.odm-merge-*'))


def test_invalid_output_does_not_replace(trial, monkeypatch):
    a, b, output = trial; output.write_bytes(b'original')
    monkeypatch.setattr(merge, '_summary', lambda *args: sample(2))
    with pytest.raises(ValueError, match='count mismatch'):
        merge.merge([a, b], output, rerun=True)
    assert output.read_bytes() == b'original'
    assert not list(output.parent.glob('.odm-merge-*'))


@pytest.mark.parametrize('mutate', [
    lambda s: s['metadata'].update(dataformat_id=3),
    lambda s: s['metadata'].update(global_encoding=17),
    lambda s: s['metadata'].update(filesource_id=42),
    lambda s: s['metadata'].update(project_id='01234567-89AB-CDEF-0123-456789ABCDEF'),
    lambda s: s['metadata'].update(system_id='OTHER'),
    lambda s: s['metadata'].update(software_id='OTHER'),
    lambda s: s['metadata'].update(vlr_1={'user_id': 'private-test', 'record_id': 42}),
    lambda s: s['metadata'].pop('vlr_0'),
    lambda s: s.update(dimensions=s['dimensions']+', ExtraDimension'),
    lambda s: s['metadata'].update(scale_x=.01),
    lambda s: s['metadata'].update(spatialreference=''),
    lambda s: s['bounds'].update(maxy=float('inf')),
    lambda s: s['bounds'].update(maxy=10**12),
    lambda s: s.update(num_points=0),
])
def test_rejects_unreviewed_clouds(mutate):
    s=copy.deepcopy(sample()); mutate(s)
    with pytest.raises(ValueError): merge._checked(s)


def test_duplicate_inputs_and_mismatched_crs(trial, monkeypatch):
    a,b,out = trial
    with pytest.raises(ValueError, match='distinct'): merge.merge([a,a], out)
    monkeypatch.setattr(merge, '_same_crs', lambda wkts: False)
    with pytest.raises(ValueError, match='Input CRS'): merge.merge([a,b], out)
    assert not out.exists()


def test_hosted_evidence_is_scoped():
    import json
    path = Path(__file__).resolve().parents[1]/'research/odm-packaged-split-merge-evidence.json'
    data = json.loads(path.read_text())
    assert data['split']['merged_points'] == 85889
    assert data['validation']['input_counts'] == [45166, 40723]
    assert not data['split']['source_overlay'] and data['split']['direct_app_scope_bypass']
    assert data['negative_pipeline']['returncode'] != 0 and data['negative_pipeline']['original_output_preserved']
    assert data['synthetic_fixture']['rejected'] == ['format', 'extra', 'precision', 'crs', 'range']


def test_raster_evidence_scope():
    import json
    path = Path(__file__).resolve().parents[1]/'research/odm-split-raster-metadata-evidence.json'
    data = json.loads(path.read_text())
    assert data['rasters'] == {'dsm': True, 'input_dsms': 2, 'input_orthos': 2, 'ortho': True}
    assert data['split']['direct_app_scope_bypass'] and not data['split']['source_overlay']
    assert data['pointcloud_validation']['merged_count'] == 81834
    assert 'not proof both contributed' in data['limitations']
