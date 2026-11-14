#!/usr/bin/env python3
"""Bounded OBJ geometry/material checks; not scientific accuracy validation."""
import argparse
import math
from pathlib import Path


def safe_child(root: Path, name: str) -> Path:
    candidate = Path(name)
    if not name or candidate.is_absolute() or '..' in candidate.parts:
        raise ValueError('Unsafe material or texture path')
    path = root/candidate
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or external material or texture')
    return path


def validate(path: Path) -> dict:
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 1024*1024*1024:
        raise ValueError('Missing or oversized OBJ')
    vertices = texcoords = faces = 0
    materials = []
    with path.open(encoding='utf-8', errors='strict') as stream:
        for line in stream:
            if len(line) > 1024*1024:
                raise ValueError('Oversized OBJ line')
            parts = line.strip().split()
            if not parts or parts[0].startswith('#'):
                continue
            if parts[0] in ('v', 'vt'):
                n = 3 if parts[0] == 'v' else 2
                if len(parts) < n+1 or not all(math.isfinite(float(v)) for v in parts[1:n+1]):
                    raise ValueError('Invalid OBJ coordinate')
                if parts[0] == 'v': vertices += 1
                else: texcoords += 1
            elif parts[0] == 'mtllib':
                if len(parts) != 2:
                    raise ValueError('Unexpected material declaration')
                materials.append(safe_child(path.parent, parts[1]))
            elif parts[0] == 'f':
                if len(parts) != 4:
                    raise ValueError('Expected triangular OBJ face')
                for token in parts[1:]:
                    fields = token.split('/')
                    if len(fields) < 2 or not fields[0] or not fields[1]:
                        raise ValueError('Missing OBJ vertex or texture index')
                    vertex, texture = int(fields[0]), int(fields[1])
                    if not (1 <= vertex <= vertices and 1 <= texture <= texcoords):
                        raise ValueError('Invalid OBJ face index')
                faces += 1
    if vertices < 3 or texcoords < 3 or faces < 1 or not materials:
        raise ValueError('Missing OBJ geometry, UVs or materials')
    textures = []
    for material in materials:
        for line in material.read_text(encoding='utf-8').splitlines():
            parts = line.strip().split(maxsplit=1)
            if parts and parts[0] == 'map_Kd':
                if len(parts) != 2:
                    raise ValueError('Invalid texture declaration')
                texture = safe_child(material.parent, parts[1])
                if texture.stat().st_size < 16:
                    raise ValueError('Empty texture')
                textures.append(texture)
    if not textures:
        raise ValueError('Missing diffuse texture')
    return {'vertices': vertices, 'texture_coordinates': texcoords, 'triangles': faces,
            'materials': len(materials), 'textures': len(textures)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('obj', type=Path)
    args = parser.parse_args()
    print(validate(args.obj))


if __name__ == '__main__':
    main()
