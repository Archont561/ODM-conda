# ODM research Python inputs: bounded source and package review

Scope: the five PyPI sdists pinned by `research/recipes/python-source-research`
and fresh linux-64 research package rebuilds. This is evidence for subsequent
qualified review, **not** a legal conclusion, complete source/notice audit,
production recipe or release approval. These private identities are not
registered release components. Their dependencies and final distribution also
need review. The sdists were downloaded from the pinned URLs, verified against
the recipe SHA256 values and examined locally; they were not committed.

| Input | Sdist SHA256 | Source observations | Key open issues |
| --- | --- | --- | --- |
| codem 0.26.1 | `e5e0f31c0da46f6087ad38e988d0c4351282d67c05f325f96c63a24f76c8dec6` | `pyproject.toml` and PKG-INFO declare Apache-2.0; root LICENSE is Apache 2.0. | Actual retained code provenance, any third-party content and required notices still need review. Upstream metadata lists only typing-extensions while the recipe explicitly declares broader observed dependencies; verify runtime completeness and downstream compatibility. |
| pygltflib 1.16.5 | `1f15740d5a7aaf71a5083e285af6b361184958e255659132f4ba8fe4f3d21ea9` | Root LICENSE is MIT with Luke Miller attribution; metadata classifier says MIT. Source includes MIT headers. | Verify retained files, notices and dependency closure; a classifier alone is not rights verification. |
| pyodm 1.5.12 | `d0433182ac6d5587786391c91d0eeafe0d78c71d618336af78964620dafe87c4` | Root LICENSE is BSD 3-Clause; `pyodm/__init__.py` points to BSD 3-Clause. The root copyright line has no named holder. | Verify attribution and provenance, dependencies, exact distributed files and notices. |
| pysolar 0.13 | `05913740694e4bb2af8412de3fa278c0435b3b15b2975c8e38625fc4eed1fd6c` | Root COPYING is GPL v3 text; multiple source headers including `pysolar/solar.py` explicitly say GPL version 3 **or later**. | Determine terms of all retained files and compatibility, provide required source/notices, review origin and runtime NumPy. A generic GPL metadata label is not a precise whole-package grant. |
| pillow-jxl-plugin 1.3.4 | `8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e` | `pyproject.toml` refers to root LICENSE, which contains GPL v3 text; the sampled project files did not establish an explicit only/or-later grant. The sdist has `Cargo.lock` with 40 registry crates, not vendored crate sources. | Establish exact grant and provenance; review 40 crate sources, native libraries, static/dynamic linkage and all applicable terms. The sdist also contains test images with separate declared terms (below). |

The later [JPEG XL crate and native review](pillow-jxl-release-review-2026-11-11.md)
adds verified locked-source and linkage evidence; the decision remains open.

### JPEG XL input and sample rights

The sdist `test/images/README.md` states that most sample images are copied
from libjxl testdata under CC-BY-4.0, identifies `bench.png` as CC-BY-SA-4.0,
and identifies `icc_profile/62AHB.jpg` as copied from Stack Overflow under
CC-BY-SA-4.0. These are upstream claims, not independent rights verification,
and do not classify every derived or associated file. Any source distribution
including the sdist needs a file-by-file provenance, attribution and
redistribution review; omission from a binary is not clearance for an archive.
The research preparation changes maturin from the upstream `vendored` feature
to `dynamic`, runs `cargo vendor --locked` and builds offline with
`--auditwheel skip`. The locked Rust crates and their notices, modifications,
actual native build/host closure and corresponding sources must be reviewed
and preserved for any distributable candidate. A lock is not itself the source.

## Fresh private package observations

[Run 42410670648](https://github.com/Archont561/ODM-conda/actions/runs/42410670648)
built and fresh-retested all five research recipes; the JPEG XL test exercises a
lossless 8×8 roundtrip, the other package tests are import checks. Outputs were
discarded and no artifact was uploaded. The [recorded package identities,
archive hashes, declared dependencies and notice-path hashes](python-research-package-evidence-2026-11-07.json)
identify these fresh builds, **not** the earlier 438-record candidate and not a
future release build. All five Conda packages still declare
`LicenseRef-Unreviewed`. Each contained a Python `.dist-info/licenses/` copy of
the corresponding root LICENSE or COPYING with a matching SHA256; this was a
filename/content-hash check, not evidence that all applicable notices are
included or that binary content has been fully audited. The inspection did not
establish complete build/host dependency identities, actual ELF/static links,
all crate licenses or corresponding-source completeness. Codem's import test
also does not exercise every declared runtime feature.

## Release blockers and next work

1. A qualified reviewer and owner must decide the exact upstream grants,
   provenance, third-party content, notices, compatibility and source-delivery
   obligations for each final package and dependency; in particular resolve the
   JPEG XL project grant, 40 crate sources and test-image rights. Preserve all
   required source, modifications, build instructions and notices in a lawful,
   durable source offer appropriate to the actual distribution.
2. Create separately versioned release recipes only after those decisions;
   set reviewed license metadata and explicit notice installation, define a
   complete source graph and stronger functional tests, then build, audit and
   validate the exact release artifacts. The private builds above are not
   publishable substitutes and these notes do not alter any gate.
3. Resolve the separate OpenMVS original-archive restrictions, OpenSfM asset
   provenance, native component gates, final solved closure and owner approval
   described in the [ODM release inventory](odm-prefix-release-readiness.md).
   Prior published component approvals do not cover these research packages.

### PyODM source comparison and offline package test

The PyPI 1.5.12 sdist was compared with the GitHub `v1.5.12` tag resolved
to commit `65ff9d0eafeef3b7cdedd4bd7915b43f53882219`. The codeload archive
SHA256 is `d50db3c4acb8cc1c0faa6bc139613ac1a130aed2376ca9ebedda97fd9f24b66e`;
the sdist hash is pinned in the recipe. All eight common regular files matched
byte-for-byte. Seven files are sdist-only (generated package metadata and
`setup.cfg`); sixteen are GitHub-only, including documentation, examples and
example images. The matched LICENSE has SHA256
`11dc23c3ed6a92475c80c466dada7b876cf44835272452dc2a0855fa173ac384`
and an unfilled copyright-holder field; `setup.py` and the sdist metadata name
“OpenDroneMap Contributors” as author, which does not itself identify every
copyright holder or establish chain of title. See
[`pyodm-source-comparison.json`](pyodm-source-comparison.json). The inputs
were inspected but not retained. The comparison does not review every file,
clear example-image rights, or establish binary/source correspondence.

The research recipe's package test now exercises URL construction, version
comparison and a mocked JSON response without network access. This is a narrow
unit smoke test, not a NodeODM integration test or production approval. Before
production packaging, verify the actual installed files, retained notices and
license provenance, review dependencies, and test the required NodeODM features.

The stronger PyODM research package test was built and fresh-retested in
[run 43484130933](https://github.com/Archont561/ODM-conda/actions/runs/43484130933).
The temporary package SHA256 was
`efcf10e8d2fd7a284e6dde6cfd735e576b422423850c418feccc70a3597c273b`;
it was discarded. This separate test does not revalidate the earlier full ODM
stack or change any release gate.

### Pysolar source comparison and additional package tests

The pinned Pysolar 0.13 sdist was compared to GitHub tag `0.13`, resolved to
commit `42a1c3311ac3df1fb906abb9723df12804a73426`; its codeload SHA256 is
`0e36673c4ab576169d339417a46a6a3485c503fe45b82519c16ec6d2bc5707b3`.
All 26 common regular files matched byte-for-byte. The sdist adds seven
generated packaging metadata files; the GitHub archive has 41 additional
files, including documentation, data and notebooks. The shared COPYING SHA256
is `864f2c1e94e559ef49f403abe8457ef8b5d7526766018b478ec796e020c5eb36`.
Sampled Python file headers state GPL version 3 or later and name multiple
authors; the generic PyPI license field is not a whole-package terms audit.
See [`pysolar-source-comparison.json`](pysolar-source-comparison.json). Inputs
were not retained. This comparison does not determine rights or clear the
additional GitHub-only assets and is not corresponding-source evidence.

The research Pysolar package test exercises equatorial equinox noon and
midnight altitude as a coarse sanity check. The pygltflib research test
round-trips a synthetic one-node scene through both glTF and GLB. These are
small offline smoke tests, not numerical-accuracy, interoperability, complete
feature, provenance, or release reviews. They do not alter release gates.
