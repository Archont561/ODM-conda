import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import PurePosixPath

base='https://coastal.er.usgs.gov/data-release/doi-P91TH157/data/'
def fetch(name, max_bytes):
    request=urllib.request.Request(base+name,headers={'User-Agent':'ODM-conda research inspection/1.0'})
    with urllib.request.urlopen(request,timeout=90) as response:
        data=response.read(max_bytes+1)
        if len(data)>max_bytes:raise ValueError('Unexpectedly large file')
        return data,response.geturl(),dict(response.headers)

data,url,headers=fetch('2017-2018_MadeiraBeachFL_GCPs.zip', 2_000_000)
with zipfile.ZipFile(io.BytesIO(data)) as z:
    files=[]
    for item in z.infolist():
        name=PurePosixPath(item.filename)
        if name.is_absolute() or '..' in name.parts or item.file_size>1000000:raise ValueError('Unexpected ZIP member')
        if item.is_dir():continue
        text=z.read(item).decode('utf-8-sig',errors='replace')
        lines=text.splitlines()
        files.append({'name':item.filename,'bytes':item.file_size,'sha256':hashlib.sha256(z.read(item)).hexdigest(),'first_lines':lines[:3], 'line_count':len(lines)})
print('::notice::GCP_INSPECTION '+json.dumps({'archive_sha256':hashlib.sha256(data).hexdigest(),'file_count':len(files)},sort_keys=True),flush=True)
for name in ('20170712_MadeiraBeachFL_UAS_Imagery.zip','20170712_MadeiraBeachFL_SfMProducts.zip'):
    url=(base+name if 'Imagery' in name else 'https://coastal.er.usgs.gov/data-release/doi-P9L474WC/data/'+name)
    request=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'ODM-conda research inspection/1.0'})
    try:
        with urllib.request.urlopen(request,timeout=90) as response:
            report={'name':name,'status':response.status,'url':response.geturl(),'content_length':response.headers.get('Content-Length'),'accept_ranges':response.headers.get('Accept-Ranges'),'etag':response.headers.get('ETag')}
    except Exception as e:report={'name':name,'error':str(e)}
    print('::notice::ARCHIVE_HEAD '+json.dumps(report,sort_keys=True),flush=True)

# Summarize surveyed checkpoints by flight, without uploading GCP files.
with zipfile.ZipFile(io.BytesIO(data)) as z:
 for item in z.infolist():
  if not item.filename.endswith('_GCPs.txt'): continue
  rows=[]; kind=None
  for line in z.read(item).decode('utf-8-sig').splitlines():
   text=line.strip()
   if text.startswith('#'):
    if 'Check Points' in text:kind='check'
    elif 'Control Points' in text:kind='control'
    continue
   fields=text.split()
   if len(fields)>=4:
    try: rows.append((fields[0],float(fields[1]),float(fields[2]),float(fields[3]),kind))
    except ValueError:pass
  near=[x for x in rows if abs(x[3])<=0.25]
  if item.filename != '20170816_GCPs.txt': continue
  print('::notice::SURVEY '+json.dumps({'file':item.filename,'rows':len(rows),'near_zero':len(near),'near_zero_checks':sum(1 for x in near if x[4]=='check'),'closest_abs_check_height':min((abs(x[3]) for x in rows if x[4]=='check'),default=None),'closest_abs_height':min((abs(x[3]) for x in rows),default=None),'types':sorted(set(str(x[4]) for x in rows))},sort_keys=True),flush=True)

metadata,url,_=fetch('MadeiraBeachFL_UAS_Imagery_metadata.txt',500000)
text=metadata.decode('utf-8',errors='replace')
print('::notice::DATUM_REVIEW '+json.dumps({'metadata_sha256':hashlib.sha256(metadata).hexdigest(),'camera_heights_agl':'heights above ground level (AGL)' in text,'camera_vertical_uncertainty_5m':'+/-5 m' in text,'image_horizontal_uncertainty_20m':'as much as 20 m' in text,'no_image_pixel_coordinates_in_gcp_header':all('im_x' not in entry['first_lines'][0] for entry in files if entry['name'].endswith('_GCPs.txt'))},sort_keys=True),flush=True)
