import pytest
np = pytest.importorskip('numpy')
from odm_raster_contribution import summarize


def test_exclusive_matching_and_overlap():
    a=np.full((1,2,4),5.);b=np.full((1,2,4),9.)
    masks=[np.array([[1,1,1,0],[1,1,1,0]],bool),np.array([[0,1,1,1],[0,1,1,1]],bool)]
    out=np.array([[[5,7,7,9],[5,7,7,9]]],float)
    result=summarize([a,b],masks,out,np.ones((2,4),bool),.01)
    assert [v['exclusive_samples'] for v in result['inputs']]==[2,2]
    assert [v['within_tolerance_fraction'] for v in result['inputs']]==[1.,1.]
    assert result['overlap_output_samples']==4
    assert result['overlap_adjacent_max_band_p95']==0
    out[0,0,0]=1
    assert summarize([a,b],masks,out,np.ones((2,4),bool),.01)['inputs'][0]['within_tolerance_fraction']==.5


def test_no_exclusive_is_not_false_proof():
    data=np.ones((1,2,2));mask=np.ones((2,2),bool)
    result=summarize([data,data],[mask,mask],data,mask,.1)
    assert all(x['exclusive_samples']==0 and x['within_tolerance_fraction'] is None for x in result['inputs'])
