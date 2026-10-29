import json
import os
import sys
from pathlib import Path
records = json.loads((Path(os.environ['RUNNER_TEMP']) / 'four-solve.json').read_text())
start, end = map(int, sys.argv[1:])
for offset in range(start, min(end, len(records)), 20):
    line = '; '.join(f"{x['file_name']} SHA256={x.get('sha256') or 'missing'}" for x in records[offset:min(offset + 20, end)])
    print(f'::notice::SOLVE {offset} {line}', flush=True)
