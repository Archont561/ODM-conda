#!/usr/bin/env python3
"""Build one native component INSIDE rattler-build's isolated environment.

Do not run this script directly. Use `pixi run build --component ...` instead.
"""
from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, config, fail_cli, first_comment, relative_path, run, source_url


def main() -> None:
    name = os.environ.get("PKG_NAME", "")
    data = config()
    if name not in data["components"]:
        raise ScaffoldError(f"Unsupported PKG_NAME: {name!r}")
    component = data["components"][name]
    if platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64"):
        raise ScaffoldError("This scaffold enables native linux-64 CPU builds only")
    for key in ("PREFIX", "SRC_DIR", "BUILD_PREFIX"):
        if not os.environ.get(key):
            raise ScaffoldError(f"Missing rattler-build environment variable: {key}")
    source = Path(os.environ["SRC_DIR"]).resolve()
    prefix = Path(os.environ["PREFIX"]).resolve()
    build_prefix = Path(os.environ["BUILD_PREFIX"]).resolve()
    if prefix == source or prefix == ROOT or prefix == Path("/") or prefix == build_prefix:
        raise ScaffoldError("Refusing an unsafe or non-isolated installation prefix")
    if os.environ.get("PKG_VERSION") != component["version"]:
        raise ScaffoldError("Recipe version and recipes/components.json disagree")
    if not (source / "CMakeLists.txt").is_file():
        raise ScaffoldError("SRC_DIR is not the expected source tree")
    if (source / ".gitmodules").exists() or component["source"]["additional_sources"]:
        raise ScaffoldError("External/submodule sources need explicit staging before this builder can support them")
    cmake_text = (source / "CMakeLists.txt").read_text(encoding="utf-8")
    if any(token in cmake_text.lower() for token in ("externalproject", "fetchcontent", "file(download")):
        raise ScaffoldError("The starter builder does not permit unstaged CMake downloads")

    # Generate notices before packaging. Preserve verbatim upstream bytes.
    generated = source / ".conda-notices"
    generated.mkdir(exist_ok=True)
    license_dir = prefix / "share" / "licenses" / name
    license_dir.mkdir(parents=True, exist_ok=True)
    for notice in component["notices"]:
        raw = relative_path(source, notice["source"]).read_bytes()
        if notice["kind"] == "first-comment":
            raw = first_comment(raw)
        elif notice["kind"] != "verbatim":
            raise ScaffoldError(f"Unsupported notice extraction: {notice['kind']}")
        destination = relative_path(generated, notice["target"])
        destination.write_bytes(raw)
        shutil.copy2(destination, license_dir / destination.name)
    shutil.copy2(ROOT / "LICENSE", generated / "packaging-MIT.txt")
    shutil.copy2(ROOT / "LICENSE", license_dir / "packaging-MIT.txt")

    env = os.environ.copy()
    # Do not let an outer Pixi environment become the host dependency prefix.
    env["CONDA_PREFIX"] = str(prefix)
    env["CMAKE_PREFIX_PATH"] = str(prefix)
    env["CMAKE_BUILD_PARALLEL_LEVEL"] = env.get("CPU_COUNT", "2")
    build_dir = source / ".native-build"
    command = [
        "cmake", "-S", str(source), "-B", str(build_dir), "-G", "Ninja",
        *shlex.split(env.get("CMAKE_ARGS", "")),
        "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={prefix}",
        f"-DCMAKE_PREFIX_PATH={prefix}", "-DCMAKE_INSTALL_LIBDIR=lib", "-DBUILD_TESTING=OFF",
    ]
    run(command, cwd=source, env=env)
    run(["cmake", "--build", str(build_dir), "--parallel", env["CMAKE_BUILD_PARALLEL_LEVEL"]], cwd=source, env=env)
    run(["cmake", "--install", str(build_dir), "--config", "Release"], cwd=source, env=env)
    executable = prefix / "bin" / component["executable"]
    if not executable.is_file():
        raise ScaffoldError(f"Expected installed executable is missing: {executable}")

    share = prefix / "share" / "odm-conda" / name
    share.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "functional_test.py", share / "functional_test.py")
    metadata = {"name": name, "version": component["version"], "build_number": component["build_number"],
                "source": component["source"], "license": component["license"], "corresponding_source": source_url(name, component)}
    (share / "upstream.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    patches = component["source"].get("patches", [])
    modified_line = (
        "Modified: yes. Local patches applied to the upstream source:\n"
        + "".join(f"  - {patch['file']} (SHA256 {patch['sha256']}): {patch['summary']}\n" for patch in patches)
        if patches else "Modified: no. Built from the unmodified upstream archive.\n"
    )
    (share / "SOURCE.txt").write_text(
        f"Unofficial {name} package\n\n"
        f"Upstream: {component['source']['repository']}\n"
        f"Commit: {component['source']['commit']}\n"
        f"Archive SHA256: {component['source']['sha256']}\n"
        f"{modified_line}"
        f"Packaging: https://github.com/{data['distribution']['repository']}\n"
        f"Corresponding source for a published build: {source_url(name, component)}\n\n"
        "This URL is populated BEFORE publication to the channel. Local/scaffold builds are not published.\n"
        "The release bundle contains the upstream archive, bundled source, notices, recipes, and build scripts.\n"
        "Upstream code and modifications retain their applicable upstream licenses.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    fail_cli(main)
