"""Shared, standard-library-only helpers for the packaging repository.

Original packaging code: MIT. Upstream sources retain their own licenses.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ("publishable", "license_reviewed", "source_completeness_reviewed", "native_validation_passed")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ScaffoldError(RuntimeError):
    """An expected validation failure, shown without a traceback by CLIs."""


def config(root: Path = ROOT) -> dict[str, Any]:
    """Read shared recipe metadata; recipe entries remain repo-root-relative."""
    return json.loads((root / "recipes/components.json").read_text(encoding="utf-8"))


def select_components(name: str, root: Path = ROOT) -> dict[str, dict[str, Any]]:
    components = config(root)["components"]
    if name == "all":
        return components
    if name not in components:
        raise ScaffoldError(f"Unknown or unimplemented component: {name!r}. Available: {', '.join(components)}")
    return {name: components[name]}


def relative_path(root: Path, value: str) -> Path:
    """Reject absolute paths, traversals, and symlinks escaping a trusted root."""
    if not value or Path(value).is_absolute() or ".." in Path(value).parts or "\\" in value:
        raise ScaffoldError(f"Unsafe relative path: {value!r}")
    result = (root / value).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ScaffoldError(f"Path escapes root: {value!r}")
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_archive(name: str, component: dict[str, Any], cache: Path) -> Path:
    """Download an immutable, hash-checked archive; never trust an unchecked cache."""
    source = component["source"]
    if source.get("additional_sources"):
        raise ScaffoldError("Source bundling for external/submodule sources is not implemented; do not publish this component yet")
    expected = source["sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ScaffoldError("Missing or malformed source checksum")
    parsed = urllib.parse.urlsplit(source["url"])
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise ScaffoldError("Source archives must use credential-free HTTPS")
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / f"{name}-{source['commit']}.tar.gz"
    if target.exists():
        if sha256(target) != expected:
            raise ScaffoldError(f"Cached source checksum mismatch: {target}; remove it and investigate")
        return target
    request = urllib.request.Request(source["url"], headers={"User-Agent": "ODM-conda-source-bundler/1"})
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as output:
            temp = Path(output.name)
            with urllib.request.urlopen(request, timeout=90) as response:
                final = urllib.parse.urlsplit(response.url)
                if final.scheme != "https":
                    raise ScaffoldError("Source download redirected away from HTTPS")
                total = 0
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    total += len(block)
                    if total > 512 * 1024 * 1024:
                        raise ScaffoldError("Source archive exceeds the scaffold's 512 MiB safety limit")
                    output.write(block)
        if sha256(temp) != expected:
            raise ScaffoldError(f"Downloaded source checksum mismatch for {name}")
        temp.replace(target)
        return target
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def first_comment(data: bytes) -> bytes:
    stripped = data.lstrip()
    if not stripped.startswith(b"/*") or b"*/" not in stripped:
        raise ScaffoldError("Expected a leading C-style license comment")
    return stripped[:stripped.index(b"*/") + 2] + b"\n"


def release_tag(name: str, component: dict[str, Any]) -> str:
    return f"{name}-v{component['version']}-b{component['build_number']}"


def source_bundle_name(name: str, component: dict[str, Any]) -> str:
    return f"source-{name}-{component['version']}-b{component['build_number']}.tar.gz"


def source_url(name: str, component: dict[str, Any], root: Path = ROOT) -> str:
    repository = config(root)["distribution"]["repository"]
    return f"https://github.com/{repository}/releases/download/{release_tag(name, component)}/{source_bundle_name(name, component)}"


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def rattler() -> str:
    found = shutil.which("rattler-build")
    if not found:
        raise ScaffoldError("rattler-build is missing. Run this command through `pixi run`.")
    return found


def find_package(name: str, component: dict[str, Any], output: Path) -> Path:
    matches = sorted((output / "linux-64").glob(f"{name}-{component['version']}-*.conda"))
    if len(matches) != 1:
        raise ScaffoldError(f"Expected exactly one {name} package in {output / 'linux-64'}, found {len(matches)}; use a clean output directory")
    return matches[0]


def repository_files(root: Path = ROOT) -> list[Path]:
    """Explicit source-bundle allowlist: no .git, credentials, caches or binaries."""
    files: list[Path] = []
    for name in ("README.md", "LICENSE", ".github/CONTRIBUTING.md", "AGENTS.md", "recipes/components.json", "pixi.toml", "pixi.lock", "pixi-sandbox.toml", "restore.sh", ".gitattributes", "recipes/variants.yaml", ".config/lefthook.yml", ".config/convco.yml", "package.json", "bun.lock", "skills-lock.json", ".gitignore"):
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ScaffoldError(f"Required packaging source is missing or a symlink: {path}")
        files.append(path)
    for folder in ("scripts", "tests", "recipes", ".github", ".agents", "backlog"):
        for path in (root / folder).rglob("*"):
            parts = set(path.relative_to(root).parts)
            excluded = {".git", "node_modules", ".cache", ".pixi", "__pycache__"}
            if parts & excluded or path.name in {".DS_Store", ".env", "local.yml", "local.yaml"} or (path.name.startswith(".env.") and path.name != ".env.example"):
                continue
            if path.is_file() and not path.is_symlink() and not path.name.endswith((".pyc", ".pyo", ".log", ".zip", ".conda", ".tar.gz", ".tar.bz2")):
                files.append(path)
    return sorted(set(files), key=lambda path: path.relative_to(root).as_posix())


def fail_cli(function: Any) -> None:
    try:
        function()
    except (ScaffoldError, OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"ERROR: {error}") from None
