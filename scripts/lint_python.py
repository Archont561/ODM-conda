#!/usr/bin/env python3
"""Fast syntax-only Python check; accepts Lefthook's staged relative file paths."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, relative_path


def check_python(paths: list[str] | None = None, root: Path = ROOT) -> int:
    files = [relative_path(root, value) for value in paths] if paths else sorted(
        path for folder in ("scripts", "tests") for path in (root / folder).rglob("*.py")
        if "__pycache__" not in path.parts
    )
    count = 0
    for path in files:
        if not path.exists():  # Deleted staged files have nothing to parse.
            continue
        if path.suffix != ".py":
            raise ScaffoldError(f"Expected a Python source file: {path}")
        try:
            ast.parse(path.read_bytes(), filename=str(path))
        except SyntaxError as error:
            raise ScaffoldError(f"Python syntax: {path}:{error.lineno}: {error.msg}") from None
        count += 1
    return count


def main() -> None:
    print(f"PASS: syntax for {check_python(sys.argv[1:])} Python source files")


if __name__ == "__main__":
    fail_cli(main)
