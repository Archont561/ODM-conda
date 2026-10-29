import re, sys
from pathlib import Path
s=Path(sys.argv[1]).read_text(errors='replace')
lines=s.splitlines()
start=next(i for i,l in enumerate(lines) if 'Cannot solve the request because of:' in l)
chunk=[]
for line in lines[start:]:
    if '::error::Combined solve/install failed' in line: break
    line=re.sub(r'^.*?\d{4}-\d\d-\d\dT\S+\s+', '', line)
    chunk.append(line)
text='\n'.join(chunk)
print('::notice::Captured solver log lines '+str(len(chunk)),flush=True)
for key in ['opensfm-odm', 'openmvs-odm', 'mvs-texturing-odm', 'libpdal-core 2.10.0', 'libopencv', 'libgdal-core 3.12.2', 'libjpeg-turbo', 'tbb 2023', 'cannot be installed because there are no viable options']:
    matching=[]
    for i,line in enumerate(chunk):
        if key in line:
            context=' | '.join(chunk[max(i-2,0):min(i+5,len(chunk))]); context=re.sub(r'\s+',' ',context)
            if context not in matching: matching.append(context)
    print('::notice::'+key+' matches '+str(len(matching))+' FIRST '+(' || '.join(matching[:2]))[:5500]+' LAST '+(' || '.join(matching[-2:]))[:5500],flush=True)
