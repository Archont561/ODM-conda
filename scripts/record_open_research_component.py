#!/usr/bin/env python3
"""Expose the selected local-only research target in the Actions UI."""
from __future__ import annotations

import os
from pathlib import Path

from common import ScaffoldError, fail_cli


def record_component(component: str, summary: Path | None = None) -> None:
    if component not in ('openmvs', 'opensfm'):
        raise ScaffoldError('Invalid research component')
    print(f'::notice title=Selected research component::{component}', flush=True)
    if summary is not None:
        with summary.open('a', encoding='utf-8') as output:
            output.write(f'### Selected research component\n\n`{component}`\n')


def main() -> None:
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    record_component(os.environ.get('RESEARCH_COMPONENT', ''), Path(summary) if summary else None)


if __name__ == '__main__':
    fail_cli(main)
