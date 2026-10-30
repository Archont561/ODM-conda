import copy
import pytest
from common import ScaffoldError
from odm_raster_sanity import validate


def fixture():
    return {'size':[10,10],'geoTransform':[1,0.1,0,2,0,-0.1], 'coordinateSystem':{'wkt':'EPSG:32617'}, 'bands':[{'type':'Byte','minimum':0,'maximum':255,'mean':100,'stdDev':10} for _ in range(4)]}


def test_valid_stats_and_rejects_bad_dimensions_transform_stats():
    assert validate(fixture())['size']==[10,10]
    for patch in ({'size':[0,1]},{'geoTransform':[0,0,0,0,0,0]},{'coordinateSystem':{}},{'bands':[]}):
        data=fixture(); data.update(patch)
        with pytest.raises(ScaffoldError): validate(data)
    data=fixture();data['bands'][0]['mean']=float('nan')
    with pytest.raises(ScaffoldError): validate(data)
