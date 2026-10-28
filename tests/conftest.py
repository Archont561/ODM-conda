"""Suite-wide pytest configuration.

Exposes scripts/ as an import path once for every test module; the previous
unittest layout repeated this insertion per file. Keep this file free of test
framework dependencies beyond pytest itself: it is imported before any module.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
