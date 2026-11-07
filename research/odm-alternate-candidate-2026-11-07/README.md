# Alternate ODM research candidate: metadata and review

This is a **metadata-only historical snapshot**, not a runnable bundle, source
offer, final release bill of materials, legal conclusion or publication
approval. It is public repository content. The private channel, 15 binaries,
source inputs, datasets and outputs were discarded; no such artifacts were
uploaded. The retained lock references a loopback channel whose exact private
archives no longer exist. Do not expect `pixi install --locked` to work from
these files alone or replace missing archives with another build of the same
name. The temporary hosted artifact is also metadata only.

## What was validated

[Run 42402466007](https://github.com/Archont561/ODM-conda/actions/runs/42402466007),
job `128493016273`, built the 15-package linux-64 research stack at commit
`d91dcec`, solved the reduced libspatialite and libarchive families, and
checked no `lzo` or `librttopo` records appeared. The 438-record environment
was replayed with an unchanged lock and matching installed identities/hashes
on a relocated private bundle. Seneca fast orthophoto and COPR with explicit
FLANN and GCP both passed the pipeline, nonempty report and raster sanity
checks; COPR exported eight GCPs, at least one with observations. These are
bounded workflow tests, not general accuracy, all-feature or production tests.
COPR's declared CC BY-SA 4.0 credits Michele M. Tobias and Alex Mandel; the
Seneca project declares CC0 with Ohio DOT attribution. Neither declaration
independently verifies granting authority.

`pixi.lock` is the generated, unmodified candidate lock; `pixi.toml` is its
manifest; `conda-inventory.json` records the installed runtime identities;
`private-bundle.json` records hashes of the private channel and metadata but
is not the channel itself; `verification.json` records the four externally
re-fetched archive hashes and the dataset commits. `SHA256SUMS` covers these
five files. The lock SHA256 is
`564066b2f3dff5666bf01df17644424748acded594b3b8d4d89704c0f04f660d`.
The private bundle manifest SHA256 is
`0b1f7e696b0eb306ae2b023aad9119cf83ce68d0fc3c096d2f1a6699a5072f37`.
The four external archives for libspatialite, libarchive, libgdal-core and
libpdal-core were independently downloaded and hashed against their installed
records. The 15 private channel package archives were hashed for the sealed
manifest and compared with the lock. Remaining external hashes are installed
record metadata; they were not independently re-downloaded and checked here.
An offline comparison also matched all 438 lock URL/SHA256 pairs against the
inventory after normalizing away the port (the inventory sanitizer drops it),
and all 15 private package hashes against the bundle manifest. This is
metadata consistency, not archive or installed-file verification. Replay
checks the retained record identities and hashes, not every installed file's
bytes or future channel availability. Build and host environments were
independently solved but not captured in this runtime inventory.

For recovery, [the metadata-only Actions artifact](https://github.com/Archont561/ODM-conda/actions/runs/42402466007/artifacts/13587726146)
expires 2026-11-21. The metadata was also relayed through
[run 42406445271](https://github.com/Archont561/ODM-conda/actions/runs/42406445271):
the deterministic transport archive SHA256 was
`75b8839878500d2138b2a51eb8d96461bb1f39d27853154251a8530d7cd0b306`;
its component checksums were verified before committing this snapshot. The
original Actions artifact ZIP has SHA256
`62ddc07ba9e55fa57943b244456ed377586e52ebfca348deaf5ad9c5a4bb3f4e`.

## Bounded source and dependency review

The runtime records all have SHA256 and license metadata, but metadata is not
source provenance, a notice audit or a legal determination. Eight records
carry `LicenseRef-Unreviewed`, including ODM, scoped OpenSfM, OpenMVS and five
research Python packages. The inventory has no filename matching its notice
heuristic for 311 records; that heuristic does not inspect package
`info/licenses` and **does not establish that notices are absent**. Review the
actual archives, bundled materials, notices, patches and source for every final
distributed dependency instead of relying on these counts.

This alternative solve is not GPL-free. Examples in its metadata include
`readline 8.3` (GPL-3.0-only), `cpd 0.5.5`, GPL-variant `ffmpeg 8.1.2`,
`x264`, `x265`, and SuiteSparse libraries with GPL terms or alternatives;
GCC runtime metadata includes exceptions. Determine the actual links, optional
plugins, distribution boundaries, applicable choices and obligations for the
final binaries; declarations alone do not settle compatibility or obligations.
The omitted LZO and librttopo packages and reduced variant labels do not clear
other dependencies or eliminate source and notice duties.

The research OpenMVS build is derived from an original archive containing
restricted IBFS/TRWS material; excluding it from the candidate does not confer
rights to distribute that original archive. Scoped OpenSfM omits vocabulary
assets and rejects BoW matching, but retained camera data and other material
still require provenance and rights review. Other private components, Python
source inputs and Cargo crates likewise require exact-source, notice, license,
security and redistribution review. See the
[ODM readiness inventory](../odm-prefix-release-readiness.md),
[Open component review](../open-components-license-review.md),
[RenderDEM source-offer preparation](../renderdem-source-offer.md), and
[alternative dependency assessment](../renderdem-alternative-dependency-assessment.md).

Before any release, retain an owner-controlled, rights-cleared corresponding
source set and exact private binary channel, capture actual build/host as well
as runtime inventories, independently verify their archive hashes and links,
replay and test the actual release binaries, and obtain a qualified review of
license compatibility, notices, source delivery and any service obligations.
The current snapshot cannot meet those requirements on its own. Component
gates and separate publication authorization remain with the owner; none were
changed here.
