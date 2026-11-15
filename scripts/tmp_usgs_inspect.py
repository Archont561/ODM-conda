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
  print('::notice::SURVEY '+json.dumps({'file':item.filename,'rows':len(rows),'near_zero':len(near),'near_zero_checks':sum(1 for x in near if x[4]=='check'),'closest_abs_height':min((abs(x[3]) for x in rows),default=None),'types':sorted(set(str(x[4]) for x in rows))},sort_keys=True),flush=True)
# Verify the two ranges needed to access ZIP entries without a multi-GB transfer.
image_url=base+'20170816_MadeiraBeachFL_UAS_Imagery.zip'
for byte_range in ('bytes=0-63','bytes=-64'):
 request=urllib.request.Request(image_url,headers={'Range':byte_range,'User-Agent':'ODM-conda research inspection/1.0'})
 try:
  with urllib.request.urlopen(request,timeout=25) as response:
   payload=response.read(64)
   result={'range':byte_range,'status':response.status,'content_range':response.headers.get('Content-Range'),'content_length':response.headers.get('Content-Length'),'sample_bytes':len(payload)}
 except Exception as exc: result={'range':byte_range,'error':type(exc).__name__+': '+str(exc)}
 print('::notice::RANGE_CHECK '+json.dumps(result,sort_keys=True),flush=True)
# Standard-library HTTP range-backed ZIP reader, bounded per read and total.
import threading
from PIL import Image, ExifTags
from pyproj import Transformer
class RangeFile(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.total=0
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  pos=offset if whence==0 else (self.pos+offset if whence==1 else self.size+offset)
  if pos<0:raise ValueError('negative seek')
  self.pos=pos;return pos
 def read(self,size=-1):
  if size<0:size=self.size-self.pos
  size=min(size,self.size-self.pos)
  if size==0:return b''
  if size>20_000_000 or self.total+size>120_000_000:raise ValueError('range budget exceeded')
  end=self.pos+size-1
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={self.pos}-{end}','User-Agent':'ODM-conda research inspection/1.0','Accept-Encoding':'identity'})
  with urllib.request.urlopen(req,timeout=60) as res:
   expected=f'bytes {self.pos}-{end}/{self.size}'
   if res.status!=206 or res.headers.get('Content-Range')!=expected:raise ValueError('invalid range response')
   payload=res.read(size+1)
  if len(payload)!=size:raise ValueError('truncated response')
  self.pos+=size;self.total+=size
  return payload
try:
 remote=RangeFile(image_url,7555083495)
 with zipfile.ZipFile(remote) as z:
  entries=[i for i in z.infolist() if i.filename.lower().endswith(('.jpg','.jpeg')) and not i.is_dir()]
  print('::notice::ZIP_INDEX '+json.dumps({'images':len(entries),'max_image_bytes':max(x.file_size for x in entries)},sort_keys=True),flush=True)
  transform=Transformer.from_crs('EPSG:4326','EPSG:26917',always_xy=True)
  with zipfile.ZipFile(io.BytesIO(data)) as gcps:
   near=[];kind=None
   for line in gcps.read('20170816_GCPs.txt').decode('utf-8-sig').splitlines():
    line=line.strip()
    if line.startswith('#'):
     if 'Check Points' in line:kind='check'
     elif 'Control Points' in line:kind='control'
     continue
    f=line.split()
    if len(f)>=4:
     try:
      x,y,h=map(float,f[1:4])
      if kind=='check' and abs(h)<=0.25:near.append((x,y))
     except ValueError:pass
  def degrees(d):return float(d[0])+float(d[1])/60+float(d[2])/3600
  samples=[]
  for i in sorted(set(round(j*(len(entries)-1)/9) for j in range(10))):
   item=entries[i]
   if item.file_size>12_000_000:raise ValueError('oversized image')
   with Image.open(io.BytesIO(z.read(item))) as im:
    gps=im.getexif().get_ifd(ExifTags.IFD.GPSInfo)
    if not all(x in gps for x in (1,2,3,4)):samples.append({'index':i,'gps':False});continue
    lat=degrees(gps[2])*(-1 if gps[1]=='S' else 1)
    lon=degrees(gps[4])*(-1 if gps[3]=='W' else 1)
    x,y=transform.transform(lon,lat)
    distance=min((((x-gx)**2+(y-gy)**2)**0.5 for gx,gy in near),default=None)
    samples.append({'index':i,'gps':True,'nearest_check_m':round(distance,1) if distance is not None else None,'width':im.width,'height':im.height})
  print('::notice::IMAGE_GPS '+json.dumps({'samples':samples,'download_bytes':remote.total},sort_keys=True),flush=True)
except Exception as exc:
 print('::notice::ZIP_PROBE_ERROR '+json.dumps({'type':type(exc).__name__,'error':str(exc)},sort_keys=True),flush=True)
