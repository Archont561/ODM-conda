import json, tempfile, urllib.request
from pathlib import Path
from inspect_dependency_source import inspect
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'cgal.tar.xz'
 urllib.request.urlretrieve('https://github.com/CGAL/cgal/releases/download/v6.2.1/CGAL-6.2.1.tar.xz',p)
 x=inspect(p,'b6be77c60765a8456335de991eeaf6ffec55256984e4a9ecc6a97c37bbfe85bf','CGAL-6.2.1')['archive']
 notices=x['notice_name_candidates']
 top={n:x['files'][n] for n in notices if '/' not in n}
 print('::notice::CGAL_INSPECTION '+json.dumps({'file_count':x['file_count'],'bytes':x['bytes'],'notice_candidate_count':len(notices),'top_level_notices':top},sort_keys=True),flush=True)
