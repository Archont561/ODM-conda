#!/usr/bin/env python3
"""Prepare a private Poisson recipe from the reduced candidate, never for release."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from common import ROOT, ScaffoldError, fail_cli, sha256
from poisson_reduced_candidate import PINNED_SHA256
from source_graph import unpack_archive


def prepare(candidate: Path, destination: Path, original: Path, root: Path = ROOT) -> dict:
    candidate, destination, original, root = Path(candidate), Path(destination), Path(original), Path(root)
    if original.is_symlink() or not original.is_file() or sha256(original) != PINNED_SHA256:
        raise ScaffoldError('Original source archive checksum mismatch')
    if candidate.is_symlink() or not candidate.is_file():
        raise ScaffoldError('Invalid candidate')
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(root.resolve()):
        raise ScaffoldError('Unsafe or existing destination')
    with tarfile.open(candidate, 'r:gz') as archive:
        members = archive.getmembers()
        if len(members) > 20000 or sum(member.size for member in members) > 256 * 1024 * 1024:
            raise ScaffoldError('Candidate exceeds size limits')
        files = {}
        for member in members:
            parts = PurePosixPath(member.name).parts
            if (not parts or member.name.startswith('/') or '\\' in member.name or '..' in parts
                    or member.name in files or not (member.isfile() or (member.isdir() and member.name == 'source/JPEG'))):
                raise ScaffoldError('Unsafe candidate member')
            files[member.name] = member
        if 'source/JPEG' not in files or 'CANDIDATE-MANIFEST.json' not in files:
            raise ScaffoldError('Missing candidate manifest or empty JPEG directory')
        stream = archive.extractfile(files['CANDIDATE-MANIFEST.json'])
        assert stream is not None
        manifest = json.load(stream)
        expected = manifest.get('files')
        if (manifest.get('scope') != 'local-research-only' or manifest.get('excluded_file_count') != 59
                or not isinstance(expected, dict) or len(manifest.get('excluded_files', {})) != 59
                or set(files) != set(expected) | {'source/JPEG', 'CANDIDATE-MANIFEST.json'}
                or any(name.startswith('source/JPEG/') for name in expected)):
            raise ScaffoldError('Unexpected candidate manifest')
        contents = {}
        for name, digest in expected.items():
            member = files[name]
            if not member.isfile() or not name.startswith(('source/', 'packaging/')):
                raise ScaffoldError('Unexpected candidate payload')
            stream = archive.extractfile(member)
            assert stream is not None
            data = stream.read()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ScaffoldError(f'Candidate file checksum mismatch: {name}')
            contents[name] = (data, member.mode & 0o777)
        # The self-reported manifest alone cannot establish origin. Compare
        # every staged source and exclusion against the hash-pinned original.
        with tempfile.TemporaryDirectory(prefix='poisson-verify-', dir=destination.parent) as temporary:
            source_tree = Path(temporary) / 'source'
            source_tree.mkdir()
            unpack_archive(original, source_tree)
            source_files = {p.relative_to(source_tree).as_posix(): sha256(p) for p in source_tree.rglob('*') if p.is_file()}
            omitted = {name: digest for name, digest in source_files.items() if name.startswith('JPEG/')}
            retained = {'source/' + name: digest for name, digest in source_files.items() if not name.startswith('JPEG/')}
            if (manifest.get('original_archive_sha256') != PINNED_SHA256 or manifest.get('excluded_files') != omitted
                    or {name: digest for name, digest in expected.items() if name.startswith('source/')} != retained):
                raise ScaffoldError('Candidate source differs from pinned original or omitted files')
        candidate_hash = sha256(candidate)
        try:
            destination.mkdir()
        except FileExistsError as error:
            raise ScaffoldError('Unsafe or existing destination') from error
        try:
            for name, (data, mode) in contents.items():
                path = destination / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(mode)
            (destination / 'source/JPEG').mkdir(parents=True, exist_ok=True)
            recipe = destination / 'packaging/recipes/poissonrecon-odm/recipe.yaml'
            text = recipe.read_text()
            old_url = '  url: https://codeload.github.com/OpenDroneMap/PoissonRecon/tar.gz/97caa6d34d1b05b59888bed019dea89ced74445e\n'
            old_sha = '  sha256: ${{ source_sha256 }}\n'
            if text.count(old_url) != 1 or text.count(old_sha) != 1:
                raise ScaffoldError('Unexpected original recipe')
            # JSON quoting is valid YAML and avoids path quoting/injection errors.
            text = text.replace(old_url, '  path: ' + json.dumps(str((destination / 'source').resolve())) + '\n').replace(old_sha, '')
            text = text.replace('  source_sha256: "88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b"\n', '')
            marker = 'build:\n  number: 3\n'
            if text.count(marker) != 1:
                raise ScaffoldError('Unexpected Poisson build identity')
            text = text.replace(marker, marker + '  string: research_${{ hash }}_3\n')
            recipe.write_text('# LOCAL RESEARCH ONLY - not a distributable recipe\n' + text)
            builder = destination / 'packaging/scripts/build_component.py'
            script = builder.read_text()
            marker = '\n\nif __name__ == "__main__":\n'
            if script.count(marker) != 1:
                raise ScaffoldError('Unexpected packaging builder')
            provenance = {'scope': 'local-research-only', 'candidate_sha256': candidate_hash,
                          'original_archive_sha256': manifest['original_archive_sha256'],
                          'excluded_file_count': 59, 'warning': 'No complete corresponding-source offer or license clearance. The original archive was fetched but is not included.'}
            injection = '\n    if name == "poissonrecon-odm":\n' + \
                '        (share / "upstream.json").write_text(' + repr(json.dumps(provenance, sort_keys=True, indent=2) + '\n') + ', encoding="utf-8")\n' + \
                '        (share / "SOURCE.txt").write_text(' + repr('LOCAL RESEARCH ONLY: reduced source candidate SHA256 ' + candidate_hash + '\nOriginal archive SHA256 ' + manifest['original_archive_sha256'] + '; original not included; 59 vendored JPEG files excluded.\nNo corresponding-source offer, release approval or legal clearance.\n') + ', encoding="utf-8")\n'
            builder.write_text(script.replace(marker, injection + marker))
            (destination / 'CANDIDATE-MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
            (destination / 'RESEARCH-PROVENANCE.json').write_text(json.dumps(provenance, sort_keys=True, indent=2) + '\n')
            return provenance
        except Exception:
            shutil.rmtree(destination)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.candidate, args.destination, args.original), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
