import csv
from pathlib import Path
import pytest
from pdal_synthetic_formats import POINTS, check_csv


def test_csv_validation_checks_all_coordinates_and_count(tmp_path):
    path=tmp_path/'points.csv'
    with path.open('w',newline='') as stream:
        writer=csv.writer(stream); writer.writerow(('X','Y','Z')); writer.writerows(POINTS)
    check_csv(path)
    path.write_text('X,Y,Z\n1,2,3\n')
    with pytest.raises(ValueError,match='points'): check_csv(path)
    with path.open('w',newline='') as stream:
        writer=csv.writer(stream); writer.writerow(('X','Y','Z')); writer.writerows([(0,0,0),*POINTS[1:]])
    with pytest.raises(ValueError,match='Unexpected'): check_csv(path)


def test_csv_validation_rejects_nonfinite_points(tmp_path):
    path=tmp_path/'points.csv'
    with path.open('w',newline='') as stream:
        writer=csv.writer(stream); writer.writerow(('X','Y','Z'))
        writer.writerows([(float('nan'), *POINTS[0][1:]), *POINTS[1:]])
    with pytest.raises(ValueError, match='Unexpected'): check_csv(path)


def test_recorded_format_evidence_is_scoped_and_identifies_selected_stack():
    import json
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/odm-pdal-synthetic-formats-evidence.json').read_text())
    assert data['fixture_results']['formats']==['las','laz','hdf','icebridge']
    assert data['fixture_results']['point_count']==3
    deps={item['name']:item for item in data['selected_dependencies']}
    assert deps['libgdal-core']['version']=='3.12.2'
    assert deps['libpdal-core']['version']=='2.10.0'
    assert deps['hdf5']['version']=='1.14.6'
    assert data['inventory_package_count']==432
    assert 'not final release lock' in data['scope']
