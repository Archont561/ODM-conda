#!/usr/bin/env python3
"""Exercise installed narrow research merge with generated LAS variants."""
import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(prefix, app):
    sys.path.insert(0, str(app))
    from opendm.conda_research_merge import merge
    pdal = prefix/'bin/pdal'
    os.environ.update({'ODM_CONDA_LOCAL_PREFIX': str(prefix), 'PROJ_DATA': str(prefix/'share/proj'),
                       'PROJ_LIB': str(prefix/'share/proj'), 'PATH': str(prefix/'bin')+os.pathsep+os.defpath})
    with tempfile.TemporaryDirectory(prefix='odm-merge-fixture-') as tmp:
        root = Path(tmp)
        def make(name, x=300000, y=4545000, srs='EPSG:32617', scale='0.001', fmt=7, extra=False):
            source=root/(name+'.csv'); output=root/(name+'.laz'); pipeline=root/(name+'.json')
            with source.open('w', newline='') as stream:
                writer=csv.writer(stream);writer.writerow(['X','Y','Z','Red','Green','Blue','Classification','Extra'])
                for i in range(10): writer.writerow([x+i*.5, y+i*.3, 220+i*.1, 1000+i, 2000+i, 3000+i, 1+i%2, 50+i])
            writer={'type':'writers.las','filename':str(output),'minor_version':4,'dataformat_id':fmt,
                    'a_srs':srs,'scale_x':scale,'scale_y':scale,'scale_z':scale,
                    'offset_x':'auto','offset_y':'auto','offset_z':'auto'}
            if extra: writer['extra_dims']='Extra=uint16'
            pipeline.write_text(json.dumps({'pipeline':[{'type':'readers.text','filename':str(source)},writer]}))
            subprocess.run([str(pdal),'pipeline',str(pipeline)],check=True)
            return output
        a=make('a');b=make('b',x=301000,y=4546000);output=root/'output.laz'
        merge([a,b],output)
        info=json.loads(subprocess.check_output([str(pdal),'info','--summary',str(output)],text=True))['summary']
        if info['num_points'] != 20: raise AssertionError('Wrong synthetic count')
        before=output.read_bytes()
        cases=[('format',make('format',fmt=3)),('extra',make('extra',extra=True)),
               ('precision',make('precision',scale='0.01')),('crs',make('crs',srs='EPSG:3857')),
               ('range',make('range',x=6000000))]
        rejected=[]
        for name, bad in cases:
            try: merge([a,bad],output,rerun=True)
            except (ValueError, subprocess.CalledProcessError): rejected.append(name)
            else: raise AssertionError(name+' was accepted')
            if output.read_bytes()!=before: raise AssertionError(name+' changed existing output')
        if list(root.glob('.odm-merge-*')): raise AssertionError('Leftover merge temporary')
        return {'point_count':info['num_points'],'rejected':rejected,'existing_output_preserved':True}


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()),sort_keys=True))
