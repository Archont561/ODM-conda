#!/usr/bin/env python3
"""Generated-data research fixture for texrecon; not package validation.

Original fixture code is MIT licensed. Invoke with an explicit executable path.
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path


def write_gradient_png(path: Path) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    width = height = 64
    raw = b"".join(b"\0" + b"".join(bytes((x * 4, y * 4, 128)) for x in range(width)) for y in range(height))
    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def test_texrecon(executable: Path, directory: Path) -> None:
    """Texture a two-triangle quad viewed from a single synthetic camera."""
    scene = directory / "scene"
    result = directory / "result"
    scene.mkdir()
    result.mkdir()
    write_gradient_png(scene / "view.png")
    (scene / "view.cam").write_text("0 0 0 1 0 0 0 1 0 0 0 1\n1 0 0 1 0.5 0.5\n", encoding="ascii")
    (directory / "mesh.ply").write_text(
        "ply\nformat ascii 1.0\nelement vertex 4\nproperty float x\nproperty float y\nproperty float z\n"
        "element face 2\nproperty list uchar int vertex_indices\nend_header\n"
        "-1 -1 4\n1 -1 4\n1 1 4\n-1 1 4\n3 0 2 1\n3 0 3 2\n", encoding="ascii")
    command = [str(executable), "--num_threads=1", "--skip_global_seam_leveling",
               "--skip_local_seam_leveling", "--no_intermediate_results", str(scene),
               str(directory / "mesh.ply"), str(result / "model")]
    completed = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, f"texrecon failed: {completed.stdout}\n{completed.stderr}"
    assert "0 faces have not been seen" in completed.stdout, completed.stdout
    model = result / "model.obj"
    material = result / "model.mtl"
    assert model.is_file() and material.is_file(), "Missing generated OBJ or material"
    lines = model.read_text(encoding="utf-8").splitlines()
    vertices = [tuple(float(v) for v in line.split()[1:]) for line in lines if line.startswith("v ")]
    faces = [line.split()[1:] for line in lines if line.startswith("f ")]
    texcoords = [line for line in lines if line.startswith("vt ")]
    assert set(vertices) == {(-1.0, -1.0, 4.0), (1.0, -1.0, 4.0), (1.0, 1.0, 4.0), (-1.0, 1.0, 4.0)}
    assert len(faces) == 2 and all(len(face) == 3 for face in faces) and texcoords, "Missing textured triangles"
    triangles = set()
    for face in faces:
        indices = [part.split("/") for part in face]
        assert all(len(part) >= 2 and part[0].isdigit() and part[1].isdigit() for part in indices), "Missing texture indices"
        assert all(1 <= int(part[0]) <= len(vertices) and 1 <= int(part[1]) <= len(texcoords) for part in indices), "Invalid OBJ indices"
        triangles.add(frozenset(vertices[int(part[0]) - 1] for part in indices))
    assert triangles == {frozenset(((-1.0, -1.0, 4.0), (1.0, 1.0, 4.0), (1.0, -1.0, 4.0))),
                         frozenset(((-1.0, -1.0, 4.0), (-1.0, 1.0, 4.0), (1.0, 1.0, 4.0)))}, "Output triangles changed"
    assert "mtllib model.mtl" in lines and any(line.startswith("usemtl ") for line in lines)
    maps = [line.split(maxsplit=1)[1] for line in material.read_text(encoding="utf-8").splitlines() if line.startswith("map_Kd ")]
    assert len(maps) == 1 and Path(maps[0]).name == maps[0], "Invalid texture map reference"
    image = result / maps[0]
    assert image.is_file(), "Missing texture image"
    data = image.read_bytes()
    assert len(data) > 32 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", "Invalid PNG texture"
    width, height = struct.unpack_from(">II", data, 16)
    assert width > 0 and height > 0, "Empty texture image"
    position = 8
    chunks = []
    compressed = bytearray()
    while position < len(data):
        assert position + 12 <= len(data), "Invalid PNG texture"
        length = struct.unpack_from(">I", data, position)[0]
        end = position + 12 + length
        assert end <= len(data), "Invalid PNG texture"
        kind = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        crc = struct.unpack_from(">I", data, position + 8 + length)[0]
        assert zlib.crc32(kind + payload) & 0xffffffff == crc, "Invalid PNG texture"
        chunks.append(kind)
        if kind == b"IDAT":
            compressed.extend(payload)
        position = end
    assert chunks and chunks[0] == b"IHDR" and chunks[-1] == b"IEND" and compressed, "Invalid PNG texture"
    try:
        decoded = zlib.decompress(compressed)
    except zlib.error as exc:
        raise AssertionError("Invalid PNG texture") from exc
    assert decoded, "Invalid PNG texture"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="texrecon-fixture-") as directory:
        test_texrecon(args.executable.resolve(), Path(directory))
    print("PASS: generated texrecon scene produced a textured quad")


if __name__ == "__main__":
    main()
