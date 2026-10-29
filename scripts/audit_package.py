#!/usr/bin/env python3
"""Audit artifact identity, dependency declarations, notices, contents and RPATH."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from common import ROOT, ScaffoldError, config, fail_cli, find_package, select_components, sha256, source_url
from package_archive import read_package
from poisson_linkage import verify_poisson_package_evidence


def audit(name: str, component: dict, package: Path, root: Path = ROOT) -> dict:
    info, payload = read_package(package)
    index = json.loads(info["info/index.json"])
    for key, expected in (("name", name), ("version", component["version"]),
                          ("build_number", component["build_number"]), ("subdir", "linux-64")):
        if index.get(key) != expected:
            raise ScaffoldError(f"Artifact {key} does not match recipes/components.json: {index.get(key)!r} != {expected!r}")
    expected_name = f"{name}-{component['version']}-{index['build']}.conda"
    if package.name != expected_name:
        raise ScaffoldError("Artifact filename does not match its internal identity")
    about = json.loads(info["info/about.json"])
    if about.get("license") != component["license"]:
        raise ScaffoldError("Artifact license metadata does not match recipes/components.json")
    runtime_names = {dependency.split()[0] for dependency in index.get("depends", [])}
    extra_runtime = {"dem2mesh": {"libgdal-core", "libgomp"}, "dem2points": {"libgdal-core"}, "fastrasterfilter": {"libgdal-core", "libgomp"},
                     "fpcfilter": {"libgomp"},
                     "mvs-texturing-odm": {"tbb", "libjpeg-turbo", "libpng", "libtiff", "libgomp"},
                     "odm-orthophoto": {"libgdal-core", "libgomp", "libopencv"}, "renderdem": {"libpdal-core", "libgomp"}, "poissonrecon-odm": {"libpng", "libjpeg-turbo", "libzlib", "libgomp"}}
    required_runtime = {"__glibc", "libgcc", "libstdcxx"} | extra_runtime.get(name, set())
    if not required_runtime.issubset(runtime_names):
        raise ScaffoldError(f"Missing declared runtime dependencies: {required_runtime - runtime_names}")
    prefix = f"share/odm-conda/{name}"
    expected = {f"bin/{component['executable']}", f"{prefix}/SOURCE.txt", f"{prefix}/upstream.json", f"{prefix}/functional_test.py",
                f"share/licenses/{name}/packaging-MIT.txt"}
    expected.update(f"share/licenses/{name}/{notice['target']}" for notice in component["notices"])
    if name == "poissonrecon-odm":
        expected.add(f"{prefix}/link-evidence.json")
    if name == "mvs-texturing-odm":
        expected.add(f"{prefix}/texrecon_fixture.py")
    missing = expected - payload.keys()
    if missing:
        raise ScaffoldError(f"Missing packaged files: {sorted(missing)}")
    # There is one native executable and an explicitly bounded documentation area.
    for path in payload:
        if not (path == f"bin/{component['executable']}" or path.startswith(f"share/licenses/{name}/") or path.startswith(prefix + "/")):
            raise ScaffoldError(f"Unexpected payload file (possible environment/source leak): {path}")
        if any(part in (".git", ".pixi", ".cache", "__pycache__") for part in PurePosixPath(path).parts):
            raise ScaffoldError(f"Build cache or checkout leaked into package: {path}")
    source_document = payload[f"{prefix}/SOURCE.txt"].decode()
    if source_url(name, component, root) not in source_document:
        raise ScaffoldError("Published corresponding-source URL is missing")
    upstream = json.loads(payload[f"{prefix}/upstream.json"])
    if upstream.get("source") != component["source"]:
        raise ScaffoldError("Packaged source manifest differs from the pinned manifest")
    metadata_notices = [path for path in info if path.startswith("info/licenses/")]
    if len(metadata_notices) < len(component["notices"]) + 1:
        raise ScaffoldError("License texts are missing from Conda's info/licenses metadata")
    checked_notices = {
        "poissonrecon-odm": ("IJG-6b-README.txt", "4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478"),
        "dem2mesh": ("Simplify-upstream-MIT.txt", "0740ee1d8869b715e5d492ec4961a415a543f4a556d79b3a9ba6fda4d38c6fd0"),
    }
    if name in checked_notices:
        target, digest = checked_notices[name]
        data = payload[f"share/licenses/{name}/{target}"]
        metadata = [info[path] for path in metadata_notices if PurePosixPath(path).name == target]
        if hashlib.sha256(data).hexdigest() != digest or len(metadata) != 1 or hashlib.sha256(metadata[0]).hexdigest() != digest:
            raise ScaffoldError(f"Missing or modified {target} in package payload or metadata")
    native = payload[f"bin/{component['executable']}"]
    if not native.startswith(b"\x7fELF"):
        raise ScaffoldError("Expected a native ELF executable")
    patchelf = shutil.which("patchelf")
    if not patchelf:
        raise ScaffoldError("patchelf is required; run the audit through Pixi")
    with tempfile.TemporaryDirectory(prefix="odm-conda-audit-") as directory:
        executable = Path(directory) / component["executable"]
        executable.write_bytes(native)
        completed = subprocess.run([patchelf, "--print-rpath", str(executable)], text=True, capture_output=True, check=True)
        rpath = completed.stdout.strip()
        needed = subprocess.run([patchelf, "--print-needed", str(executable)], text=True, capture_output=True, check=True).stdout.splitlines()
        if name == "poissonrecon-odm":
            evidence = json.loads(payload[f"{prefix}/link-evidence.json"])
            verify_poisson_package_evidence(evidence, needed)
        for entry in rpath.split(":"):
            if entry and not (entry.startswith("$ORIGIN/") or entry.startswith("${ORIGIN}/") or entry in ("$ORIGIN", "${ORIGIN}")):
                raise ScaffoldError(f"Non-relocatable ELF RPATH: {entry!r}")
    return {"component": name, "artifact": package.name, "sha256": sha256(package),
            "license": component["license"], "payload_files": len(payload), "metadata_license_files": len(metadata_notices),
            "runtime_dependencies": index["depends"], "elf_needed": needed, "rpath": rpath, "source_commit": component["source"]["commit"],
            "result": "passed", "scope": "Artifact audit only; not a complete license or ODM integration review"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--reports-dir", type=Path, default=ROOT / "reports")
    options = parser.parse_args()
    options.reports_dir.mkdir(parents=True, exist_ok=True)
    for name, component in select_components(options.component).items():
        package = find_package(name, component, options.output_dir)
        report = audit(name, component, package)
        path = options.reports_dir / f"audit-{name}.json"
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"PASS: {name} artifact audit -> {path}")


if __name__ == "__main__":
    fail_cli(main)
