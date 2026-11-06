import os
from pathlib import Path
p = Path(os.environ['RUNNER_TEMP'])/'renderdem-output'
for meta in sorted(p.rglob('conda-meta')):
    print(f'::notice::PREFIX {meta.relative_to(p)} count={len(list(meta.glob("*.json")))}', flush=True)
