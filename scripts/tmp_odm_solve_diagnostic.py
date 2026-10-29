import re, sys
from pathlib import Path
lines=Path(sys.argv[1]).read_text(errors='replace').splitlines()
start=next(i for i,l in enumerate(lines) if 'Cannot solve the request because of:' in l)
chunk=[]
for line in lines[start:]:
    if '::error::Combined solve/install failed' in line: break
    line=re.sub(r'^.*?\d{4}-\d\d-\d\dT\S+\s+', '', line)
    chunk.append(line.strip())
for i in range(0,len(chunk),30):
    print('::notice::SOLVER PART '+str(i//30+1)+': '+' | '.join(chunk[i:i+30]),flush=True)
