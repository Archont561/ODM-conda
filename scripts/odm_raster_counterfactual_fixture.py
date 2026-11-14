#!/usr/bin/env python3
"""Small controlled ODM raster merges, including source-ablation counterfactuals."""
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.enums import ColorInterp


def run(prefix, app):
    os.environ['ODM_CONDA_LOCAL_PREFIX']=str(prefix)
    sys.path.insert(0,str(app))
    from opendm.orthophoto import merge as merge_ortho
    from opendm.dem.merge import euclidean_merge_dems
    with tempfile.TemporaryDirectory(prefix='odm-raster-ablation-') as d:
        root=Path(d); H=32; W=24
        def save(name, array, x, nodata=None):
            p=root/name
            with rasterio.open(p,'w',driver='GTiff',width=W,height=H,count=array.shape[0],dtype=str(array.dtype),crs='EPSG:32617',transform=from_origin(x,32,1,1),nodata=nodata) as out:
                out.write(array)
                if array.shape[0]==4:out.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue,ColorInterp.alpha)
            return p
        def inputs(enabled):
            pairs=[];dems=[]
            for idx,(x,value,alpha) in enumerate([(0,100,255),(8,200,128)]):
                image=np.full((4,H,W),value,dtype=np.uint8);image[3,:,:]=alpha if enabled[idx] else 0
                cut=np.zeros_like(image)
                ortho=save(f'ortho-{enabled}-{idx}.tif',image,x);cutpath=save(f'cut-{enabled}-{idx}.tif',cut,x)
                pairs.append((str(ortho),str(cutpath)))
                arr=np.full((1,H,W),float(value) if enabled[idx] else -9999,dtype=np.float32)
                dem=save(f'dem-{enabled}-{idx}.tif',arr,x,-9999);dems.append(str(dem))
                save(f'dem-{enabled}-{idx}.euclideand.tif',np.full((1,H,W),10,dtype=np.float32),x,0)
            return pairs,dems
        def produce(label,enabled,reverse=False):
            pairs,dems=inputs(enabled)
            if reverse:pairs.reverse();dems.reverse()
            ortho=root/(label+'-ortho.tif');dem=root/(label+'-dem.tif')
            merge_ortho(pairs,str(ortho),{'TILED':'NO'})
            euclidean_merge_dems(dems,str(dem),{'TILED':'NO'})
            with rasterio.open(ortho) as o,rasterio.open(dem) as h:
                if o.crs.to_epsg()!=32617 or h.crs.to_epsg()!=32617 or o.shape!=(32,32) or h.shape!=(32,32):raise AssertionError('Unexpected geometry')
                return o.read(),h.read(1)
        both_o,both_h=produce('both',(True,True))
        first_o,first_h=produce('first',(True,False))
        second_o,second_h=produce('second',(False,True))
        reverse_o,reverse_h=produce('reverse',(True,True),True)
        if not np.all(both_o[3]==255):raise AssertionError('Missing orthophoto union coverage')
        if not np.all(both_h!=-9999):raise AssertionError('Missing DEM union coverage')
        # Check full images, not just a few points: exclusive source values,
        # arithmetic mean in equal-weight DEM overlap, and ortho ablations.
        if not np.all(first_o[3,:,:24]>0) or np.any(first_o[3,:,24:]):raise AssertionError('First source coverage wrong')
        if np.any(second_o[3,:,:8]) or not np.all(second_o[3,:,8:]>0):raise AssertionError('Second source coverage wrong')
        if not np.all(first_h[:,:24]==100) or not np.all(second_h[:,8:]==200):raise AssertionError('DEM ablation incorrect')
        if not np.allclose(both_h[:,:8],100) or not np.allclose(both_h[:,8:24],150) or not np.allclose(both_h[:,24:],200):raise AssertionError('DEM blend incorrect')
        if not np.allclose(reverse_h,both_h):raise AssertionError('DEM order changed output')
        if not np.all(both_o[0,:,:8]==100) or not np.all(both_o[0,:,24:]==200):raise AssertionError('Ortho exclusive values incorrect')
        report={'shape':[32,32],'coverage_pixels':int((both_o[3]>0).sum()),
          'dem_exclusive_values':[float(both_h[0,0]),float(both_h[0,31])], 'dem_overlap_value':float(both_h[0,12]),
          'ortho_overlap_values':sorted(int(v) for v in np.unique(both_o[0,:,8:24])),
          'ortho_reversed_overlap_values':sorted(int(v) for v in np.unique(reverse_o[0,:,8:24])),
          'ortho_ablation_changed_pixels':[int(np.count_nonzero(both_o[0]!=first_o[0])),int(np.count_nonzero(both_o[0]!=second_o[0]))],
          'dem_ablation_changed_pixels':[int(np.count_nonzero(both_h!=first_h)),int(np.count_nonzero(both_h!=second_h))],
          'ortho_order_changed_pixels':int(np.count_nonzero(both_o[0]!=reverse_o[0]))}
        if not all(v>0 for v in report['ortho_ablation_changed_pixels']+report['dem_ablation_changed_pixels']):raise AssertionError('Source ablation had no effect')
        return report


if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()),sort_keys=True))
