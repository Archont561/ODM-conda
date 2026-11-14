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
  return {**{k:data.get(k) for k in keys},'vlr_keys':[k for k in data if 'vlr' in k.lower()]}
 flags={'global_encoding':1,'filesource_id':42,'project_id':'01234567-89ab-cdef-0123-456789abcdef','system_id':'EXPERIMENT','software_id':'EXPERIMENT','creation_doy':7,'creation_year':2021,'vlrs':[{'user_id':'private-test','record_id':42,'description':'synthetic','data':'Zm9v'}]}
 a=create('a',flags);b=create('b',flags);out=root/'merged.laz';merge([a,b],out)
 print('::notice::METADATA_RESULT '+json.dumps({'input':concise(a),'output':concise(out)},sort_keys=True),flush=True)
