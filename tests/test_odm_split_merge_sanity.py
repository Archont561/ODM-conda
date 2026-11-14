import pytest
from odm_split_merge_sanity import DIMENSIONS, compare_rows


def row():
    return {name: '1' for name in DIMENSIONS}


def test_merge_rows_counts_coordinates_and_attributes():
    a, b = row(), row(); b['X'] = '1.001'
    assert compare_rows([a], [b]) == 1
    b['X'] = '1.01'
    with pytest.raises(ValueError, match='X differs'):
        compare_rows([a], [b])
    b = row(); b['Classification'] = '2'
    with pytest.raises(ValueError, match='Classification differs'):
        compare_rows([a], [b])
    with pytest.raises(ValueError, match='count'):
        compare_rows([a], [])
    b = row(); b['Z'] = 'nan'
    with pytest.raises(ValueError, match='Nonfinite'):
        compare_rows([a], [b])
