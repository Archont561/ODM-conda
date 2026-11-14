#!/usr/bin/env python3
"""Private LAS metadata guard fixture; run with the PDAL/GDAL prefix Python."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from odm_research_merge import merge
prefix=Path(sys.prefix);pdal=prefix/'bin/pdal'
os.environ.update(ODM_CONDA_LOCAL_PREFIX=str(prefix),PROJ_DATA=str(prefix/'share/proj'),PROJ_LIB=str(prefix/'share/proj'),PATH=str(prefix/'bin')+os.pathsep+os.defpath)
with tempfile.TemporaryDirectory() as d:
 root=Path(d);source=root/'points.csv';source.write_text('X,Y,Z,Red,Green,Blue,GpsTime\n300000,4545000,200,1,2,3,1000\n300001,4545001,201,4,5,6,1001\n')
 def create(name, flags):
  dest=root/(name+'.laz'); pipe=root/(name+'.json')
  writer={'type':'writers.las','filename':str(dest),'minor_version':4,'dataformat_id':7,'a_srs':'EPSG:32617','scale_x':.001,'scale_y':.001,'scale_z':.001,'offset_x':'auto','offset_y':'auto','offset_z':'auto',**flags}
  pipe.write_text(json.dumps({'pipeline':[{'type':'readers.text','filename':str(source)},writer]}));subprocess.run([str(pdal),'pipeline',str(pipe)],check=True)
  return dest
 def metadata(p):
  return json.loads(subprocess.check_output([str(pdal),'info','--summary',str(p)],text=True))['summary']['metadata']
 def concise(p):
  data=metadata(p);keys=['filesource_id','global_encoding','project_id','system_id','software_id','creation_doy','creation_year']
  return {**{k:data.get(k) for k in keys},'vlrs':{k:{kk:vv for kk,vv in v.items() if kk not in ('data','data_base64')} for k,v in data.items() if k.startswith('vlr_') and isinstance(v,dict)}}
 a=create('a',{});b=create('b',{});out=root/'merged.laz';merge([a,b],out);original=out.read_bytes()
 custom={'user_id':'private-test','record_id':42,'description':'synthetic','data':'Zm9v'}
 cases={'gps_encoding':{'global_encoding':1},'source_id':{'filesource_id':42},'project_id':{'project_id':'01234567-89ab-cdef-0123-456789abcdef'},'system_id':{'system_id':'EXPERIMENT'},'software_id':{'software_id':'EXPERIMENT'},'custom_vlr':{'vlrs':[custom]},'custom_evlr':{'vlrs':[{**custom,'evlr':True}]}}
 rejected={}
 for key,flags in cases.items():
  candidate=create(key,flags)
  try:merge([a,candidate],out,rerun=True)
  except ValueError as e: rejected[key]=str(e)
  else: raise AssertionError(key+' silently accepted')
  if out.read_bytes()!=original:raise AssertionError(key+' modified existing output')
 print('::notice::METADATA_GUARD '+json.dumps({'rejected':rejected,'existing_output_preserved':True,'baseline_input':concise(a),'output':concise(out)},sort_keys=True),flush=True)
