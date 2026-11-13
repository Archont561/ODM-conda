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
