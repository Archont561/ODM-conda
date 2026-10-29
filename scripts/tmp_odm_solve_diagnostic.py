import subprocess,tempfile
from pathlib import Path
specs=['pdal ==2.10.0','libgdal-core ==3.12.2','gflags >=2.2.2,<2.3','eigen >=3.4,<4','libjpeg-turbo >=3.2.1,<4','python >=3.12,<3.13','ceres-solver','py-opencv >=4.12,<4.13','tbb >=2023.1,<2024','python-pdal','gdal','exiftool','numpy','suitesparse','glog','libgomp >=14','rasterio','rawpy','cloudpickle','exifread','flask','fpdf2','joblib','matplotlib','networkx','pillow','pyproj','python-dateutil','pyyaml','scipy','six','xmltodict','beautifulsoup4','lxml','libboost >=1.90,<1.91','mpfr','gmp','libpng >=1.6.59,<1.7','libtiff']
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'environment';subprocess.run(['pixi','init','--format','pixi','--scm','github','-c','conda-forge','-p','linux-64',str(p)],check=True,capture_output=True)
 r=subprocess.run(['pixi','add','--manifest-path',str(p/'pixi.toml'),'--no-install',*specs],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if r.returncode:
  print('::error::Expanded dependency-only solve failed: '+r.stdout[:9500].replace('\n',' | '),flush=True);raise SystemExit(1)
 rows=subprocess.run(['pixi','list','--manifest-path',str(p/'pixi.toml'),'--locked','--no-install'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
 print('::notice::Expanded dependency-only solve PASS: '+' | '.join(x.strip() for x in rows.splitlines() if any(y in x for y in ('gflags','eigen','libpdal-core','pdal ','libgdal-core','ceres-solver','libopencv'))),flush=True)
