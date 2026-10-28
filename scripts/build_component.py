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

from common import ROOT, ScaffoldError, config, fail_cli, first_comment, relative_path, run, sha256, source_url
from openmvs_graph_policy import validate_openmvs_graph, validate_openmvs_patches, verify_openmvs_tree
from texturing_graph_policy import validate_texturing_graph, validate_texturing_patches, verify_texturing_tree
from texturing_link_map import verify_texturing_link_map


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
    build_file = "Makefile" if name == "poissonrecon-odm" else "CMakeLists.txt"
    if not (source / build_file).is_file():
        raise ScaffoldError("SRC_DIR is not the expected source tree")
    if name == "openmvs-odm":
        validate_openmvs_graph(name, component["source"])
        validate_openmvs_patches(component["source"])
        verify_openmvs_tree(source)
    elif name == "mvs-texturing-odm":
        validate_texturing_graph(name, component["source"])
        validate_texturing_patches(component["source"])
        verify_texturing_tree(source)
    elif (source / ".gitmodules").exists() or component["source"]["additional_sources"]:
        raise ScaffoldError("External/submodule sources need explicit staging before this builder can support them")
    if build_file == "CMakeLists.txt":
        cmake_text = (source / build_file).read_text(encoding="utf-8")
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
    if name == "openmvs-odm":
        # The fingerprint above permits only the patched, reduced ReconstructMesh
        # tree. Keep bundled Eigen header-only and do not install other apps or
        # upstream libraries/headers from this intentionally reduced build.
        command.extend([
            f"-DVCG_ROOT={source / '_external' / 'vcg'}",
            f"-DEIGEN3_INCLUDE_DIR={source / '_external' / 'eigen'}",
            "-DOpenMVS_USE_CUDA=OFF", "-DOpenMVS_USE_OPENGL=OFF", "-DOpenMVS_USE_BREAKPAD=OFF",
            "-DOpenMVS_USE_CERES=OFF", "-DOpenMVS_USE_PYTHON=OFF", "-DOpenMVS_ENABLE_TESTS=OFF",
            "-DENABLE_SSE3=OFF", "-DENABLE_SSSE3=OFF", "-DENABLE_SSE41=OFF", "-DENABLE_SSE42=OFF",
            "-DENABLE_AVX=OFF", "-DENABLE_AVX2=OFF",
            f"-DCMAKE_CXX_FLAGS={env.get('CXXFLAGS', '')} -march=x86-64 -mno-popcnt -DEIGEN_MPL2_ONLY",
        ])
        run(command, cwd=source, env=env)
        run(["cmake", "--build", str(build_dir), "--target", "ReconstructMesh", "--parallel", "2"], cwd=source, env=env)
        (prefix / "bin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(build_dir / "bin" / "ReconstructMesh", prefix / "bin" / "ReconstructMesh")
    elif name == "mvs-texturing-odm":
        # Build MVE from the verified, patched graph rather than relying on
        # ExternalProject or an ambient MVE installation.
        mve_source = source / '_external' / 'mve'
        mve_build = source / '.native-mve'
        baseline = f"{env.get('CXXFLAGS', '')} -march=x86-64 -mno-popcnt"
        mve_command = [
            "cmake", "-S", str(mve_source), "-B", str(mve_build), "-G", "Ninja",
            *shlex.split(env.get("CMAKE_ARGS", "")), "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_PREFIX_PATH={prefix}", f"-DCMAKE_CXX_FLAGS={baseline}",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5", "-DBUILD_SHARED_LIBS=OFF",
        ]
        run(mve_command, cwd=source, env=env)
        run(["cmake", "--build", str(mve_build), "--target", "mve", "mve_util", "mve_sfm", "mve_dmrecon", "--parallel", "2"], cwd=source, env=env)
        # Capture the actual GNU linker inputs before rattler strips the binary.
        # This tests named link inputs, not source redistribution or patent rights.
        link_map = build_dir / 'texrecon-link.map'
        link_flags = f"{env.get('LDFLAGS', '')} -Wl,-Map={link_map}"
        command.extend([
            f"-DCMAKE_EXE_LINKER_FLAGS={link_flags}",
            f"-DMVE_ROOT={mve_source}", f"-DCMAKE_CXX_FLAGS={baseline}", "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
            f"-DMVE_MVE_LIBRARY_RELEASE={mve_build / 'libs' / 'mve' / 'libmve.a'}",
            f"-DMVE_UTIL_LIBRARY_RELEASE={mve_build / 'libs' / 'util' / 'libmve_util.a'}",
            f"-DMVE_SFM_LIBRARY_RELEASE={mve_build / 'libs' / 'sfm' / 'libmve_sfm.a'}",
            f"-DMVE_DMRECON_LIBRARY_RELEASE={mve_build / 'libs' / 'dmrecon' / 'libmve_dmrecon.a'}",
        ])
        run(command, cwd=source, env=env)
        run(["cmake", "--build", str(build_dir), "--target", "texrecon", "--parallel", "2"], cwd=source, env=env)
        digest = verify_texturing_link_map(link_map)
        print(f"PASS: texrecon link map excludes named MVE SIFT/SURF inputs; SHA256 {digest}", flush=True)
        (prefix / "bin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(build_dir / "apps" / "texrecon" / "texrecon", prefix / "bin" / "texrecon")
    elif name == "poissonrecon-odm":
        # Restrict make execution to the two specifically reviewed files from
        # the pinned archive; source changes require another fetch-command review.
        makefiles = {"Makefile": "133c7df53d2d4c0dc3126c73b7b5f997a4930f355de8385649391e6813e1d5a5",
                     "PNG/Makefile": "7adc41995370ce48374fdf79be2143af94311f0bf0abe4fd6462b111d19d4d06"}
        for filename, expected in makefiles.items():
            if sha256(relative_path(source, filename)) != expected:
                raise ScaffoldError(f"Unreviewed makefile: {filename}")
        # Upstream's makefiles assign CC/CXX directly, so pass the isolated
        # compiler wrappers as command-line variables (also inherited by PNG).
        cc, cxx = env.get("CC"), env.get("CXX")
        if not cc or not cxx:
            raise ScaffoldError("PoissonRecon requires rattler's C and C++ compiler wrappers")
        flags = env.get("CXXFLAGS", "") + " -fopenmp -Wno-deprecated -std=c++14 -pthread -Wno-invalid-offsetof -O3 -DRELEASE -ffast-math -g0"
        links = env.get("LDFLAGS", "") + " -lgomp -lstdc++ -lpthread -O3 -g0"
        run(["make", "-j1", "poissonrecon", f"CC={cc}", f"CXX={cxx}", f"CFLAGS={flags}", f"LFLAGS={links}"], cwd=source, env=env)
        (prefix / "bin").mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / "Bin" / "Linux" / "PoissonRecon", prefix / "bin" / "PoissonRecon")
    else:
        run(command, cwd=source, env=env)
        run(["cmake", "--build", str(build_dir), "--parallel", env["CMAKE_BUILD_PARALLEL_LEVEL"]], cwd=source, env=env)
        run(["cmake", "--install", str(build_dir), "--config", "Release"], cwd=source, env=env)
    executable = prefix / "bin" / component["executable"]
    if not executable.is_file():
        raise ScaffoldError(f"Expected installed executable is missing: {executable}")

    share = prefix / "share" / "odm-conda" / name
    share.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "functional_test.py", share / "functional_test.py")
    if name == "openmvs-odm":
        for fixture in ("openmvs_synthetic_fixture.py", "openmvs_pointcloud_fixture.py", "texrecon_fixture.py"):
            shutil.copy2(ROOT / "scripts" / fixture, share / fixture)
    elif name == "mvs-texturing-odm":
        shutil.copy2(ROOT / "scripts" / "texrecon_fixture.py", share / "texrecon_fixture.py")
    metadata = {"name": name, "version": component["version"], "build_number": component["build_number"],
                "source": component["source"], "license": component["license"], "corresponding_source": source_url(name, component)}
    (share / "upstream.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    patches = component["source"].get("patches", [])
    modified_line = (
        "Modified: yes. Local patches applied to the upstream source:\n"
        + "".join(f"  - {patch['file']} (SHA256 {patch['sha256']}, target {patch.get('target', '.')}): {patch['summary']}\n" for patch in patches)
        if patches else "Modified: no. Built from the unmodified upstream archive.\n"
    )
    additional_line = "".join(
        f"Additional source: {item['name']} at {item['path']}\n"
        f"  URL: {item['url']}\n  Commit: {item['commit']}\n  SHA256: {item['sha256']}\n"
        for item in component['source'].get('additional_sources', [])
    )
    (share / "SOURCE.txt").write_text(
        f"Unofficial {name} package\n\n"
        f"Upstream: {component['source']['repository']}\n"
        f"Commit: {component['source']['commit']}\n"
        f"Archive SHA256: {component['source']['sha256']}\n"
        f"{additional_line}"
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
