#!/usr/bin/env python3
"""Research-only OpenSfM native-binding smoke test, not an installed dataset test."""
from __future__ import annotations

import argparse
import importlib
import importlib.machinery
import math
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="directory containing the opensfm package")
    source = parser.parse_args().source.resolve()
    sys.path.insert(0, str(source))
    names = ("pygeo", "pygeometry", "pyrobust", "pybundle", "pyfeatures", "pydense", "pysfm", "pymap")
    modules = {}
    try:
        for name in names:
            module = importlib.import_module("opensfm." + name)
            path = Path(module.__file__).resolve()
            if not path.is_relative_to(source) or not any(path.name.endswith(s) for s in importlib.machinery.EXTENSION_SUFFIXES):
                raise ImportError(f"{name} is not a native extension in the specified tree")
            modules[name] = module
    except (ImportError, AttributeError) as error:
        raise SystemExit(f"OpenSfM native bindings unavailable: {error}") from error
    position = modules["pygeo"].ecef_from_lla(0.0, 0.0, 0.0)
    assert len(position) == 3 and all(math.isclose(float(a), b, abs_tol=1e-6) for a, b in zip(position, (6378137.0, 0.0, 0.0)))
    lat_lon_alt = modules["pygeo"].lla_from_ecef(*position)
    assert all(math.isclose(float(value), 0.0, abs_tol=1e-6) for value in lat_lon_alt)
    pose = modules["pygeometry"].Pose()
    assert pose.is_identity(1e-12)
    assert all(math.isclose(float(a), b, abs_tol=1e-6) for a, b in zip(pose.transform([1.0, 2.0, 3.0]), (1.0, 2.0, 3.0)))
    from opensfm.transformations import angle_between_vectors
    assert math.isclose(angle_between_vectors([1, 0, 0], [0, 1, 0]), math.pi / 2)
    from matplotlib import cm
    assert cm.get_cmap("viridis_r") is not None
    print("PASS: research OpenSfM native imports and geometry smoke test")


if __name__ == "__main__":
    main()
