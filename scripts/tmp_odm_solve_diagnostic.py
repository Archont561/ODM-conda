import subprocess,tempfile
from pathlib import Path
cases = {
 'new-gflags':['pdal ==2.10.0','libgdal-core ==3.12.2','gflags >=2.3.1,<2.4','libjpeg-turbo >=3.2.1,<4','python >=3.12,<3.13'],
 'old-gflags':['pdal ==2.10.0','libgdal-core ==3.12.2','gflags >=2.2,<2.3','libjpeg-turbo >=3.2.1,<4','python >=3.12,<3.13','ceres-solver','py-opencv >=4.12,<4.13','tbb >=2023.1,<2024','python-pdal','gdal'],
 'new-no-pdal':['libpdal-core ==2.10.0','libgdal-core ==3.12.2','gflags >=2.3.1,<2.4','libjpeg-turbo >=3.2.1,<4','python >=3.12,<3.13','ceres-solver'],
}
with tempfile.TemporaryDirectory() as temp:
 for name,specs in cases.items():
  p=Path(temp)/name
  subprocess.run(['pixi','init','--format','pixi','--scm','github','-c','conda-forge','-p','linux-64',str(p)],check=True,capture_output=True)
  r=subprocess.run(['pixi','add','--manifest-path',str(p/'pixi.toml'),'--no-install',*specs],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  if r.returncode: print('::notice::'+name+' FAIL: '+r.stdout[:6500].replace('\n',' | '),flush=True)
  else:
   rows=subprocess.run(['pixi','list','--manifest-path',str(p/'pixi.toml'),'--locked','--no-install'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
   print('::notice::'+name+' PASS: '+' | '.join(x.strip() for x in rows.splitlines() if any(y in x for y in ('gflags','libpdal-core','pdal ','libgdal-core','ceres-solver','libjpeg-turbo'))),flush=True)
