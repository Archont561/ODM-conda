# OpenMVS TetraFlow alternative: private feasibility trial

This is **not** a production recipe, a legal conclusion, or an authorization to
publish. The historical ODM fork archive still contains restricted IBFS/TRWS
sources. No existing source, binary, release or audit gate is relaxed here.

## Candidate and scope

[OpenMVS commit 0aebb63a7dc72f2831615b441fdf2f474d7a0ea0](https://github.com/OpenDroneMap/openMVS/commit/0aebb63a7dc72f2831615b441fdf2f474d7a0ea0)
removes IBFS and replaces it with `libs/Math/TetraFlow.h`. At this commit the
Git tree has no files under `libs/Math/IBFS` or `libs/Math/TRWS`. The header
states Boost Software License 1.0 and says the implementation is independent
and no existing max-flow source was consulted. These are upstream assertions,
not independent provenance verification or a clearance of the whole tree.
Codeload archive SHA-256: `4701b4490c8036bc548f23b949d871bd2c133386051aad051d1f3de912b26014`.

This commit is on the fork's develop line, not the pinned ODM master revision.
The two histories diverge substantially: 471 files changed in the tree diff,
including ODM-specific changes and upstream changes. It is not a drop-in
replacement merely because the graph solver changed. In particular, this
upstream `ReconstructMesh` lacks the previously developed explicit visibility
validation; its point-cloud reader differs from the hardened ODM research
patch. A research patch now ports bounded visibility, list-schema, byte-order
and allocation checks, including matching view-weight counts. The generated
positive and negative fixtures passed in the private trial below. Do not use it
with untrusted or malformed PLY inputs; the patch is not a comprehensive parser
security review.

## Experiment

The isolated linux-64 `research/recipes/openmvs-tetraflow-research/recipe.yaml`
builds only `ReconstructMesh`, excluding three dense/refine/texture translation
units and unrelated SFM apps. The build checks exact hashes of the changed
source inputs, rejects the named restricted directories, and applies the
existing named link-map check to a static-library link. Neither this check nor
absence of those directory names establishes complete provenance, rights,
source coverage or absence of restricted material elsewhere.

A temporary GitHub runner build and separate package retest
[43092563761](https://github.com/Archont561/ODM-conda/actions/runs/43092563761)
passed, including reconstruction of the repository's generated two-camera
scene. Package SHA-256 was
`2b4de6a38722d9a2e1ccb7ecf0217beb164243722dfdae9ff7702e0a62b60f85`.
The research sources and binary were discarded with the job; only the hash
was retained. That run predates the visibility patch and extended fixtures.
This does not test ODM integration, all command-line options,
mesh quality, separate PLY loading, real-world scenes, or full OpenMVS.
Conda dependencies were solved online, not against a retained final lock.

To repeat privately on a trusted host, use `rattler-build build --recipe
research/recipes/openmvs-tetraflow-research/recipe.yaml --target-platform
linux-64 --variant-config recipes/variants.yaml --channel conda-forge
--channel-priority strict --output-dir <private-directory>` and independently
retest the resulting package. The build script expects the repository checkout;
never upload its output or source without approval.

## Remaining work before a production candidate

1. Independently review the exact source archive, TetraFlow authorship and all
   included third-party sources/notices; owner decides rights and policy. The
   upstream commit metadata identifies cDc as author, while the header claims
   independent authorship; neither establishes the complete chain of rights.
   The upstream `COPYRIGHT.md` lists AGPL for OpenMVS and multiple third-party
   licenses, including CGAL, Eigen, LMFit and Boost; it is not a verified BOM.
   Its design notes explicitly discuss research-only IBFS alternatives, which
   is contextual commentary, not proof about every file in the archive.
2. Independently review the research PLY/visibility patch, and test further
   malformed and realistic inputs. Verify ODM-required formats and behavior.
3. Test with scoped OpenSfM and ODM end-to-end on suitably cleared data, and
   assess functionality/quality relative to the historical fork. Review all
   other ODM-specific changes lost across the diverged histories.
4. Finish OpenSfM asset and JPEG XL project/native/source reviews; assemble
   complete source/notice obligations for the actual selected closure.
5. Build and retain the final exact packages, source materials, inventory and
   replay lock in owner-controlled storage; replay and audit them. Owner must
   approve gates and dispatch the release workflow before publication.

## Standalone upstream solver test

With GCC 12.2 on linux-64, `python scripts/test_tetraflow_reference.py
<extracted-pinned-source>` compiled the exact pinned TetraFlow header and the
upstream `TestsMath.cpp` test body in a temporary standalone harness, with
assertions enabled. All 400 deterministic randomized graphs matched the
upstream Edmonds–Karp reference and cut capacity checks. The harness replaces
only the upstream test includes and logging/assertion macros; input hashes are
verified first. This is the upstream test, not an independent test design. It
is not a build or test of the patched ReconstructMesh, ODM integration, rights,
source completeness, numerical quality on real scenes, or security.

## ODM cleanup compatibility probe (static, not integration)

The SHA-256-verified ODM 3.6.2 source pinned in the research recipe calls
`ReconstructMesh` in `opendm/mesh.py` for both gridded DEM and Poisson mesh
cleanup. Both pass `-i`, `-o`, `--archive-type 3`, `--remove-spikes 0`,
`--smooth 0`, `--target-face-num`, and `-v 0`; the `--remove-spurious` value
is respectively 0 and 20. The TetraFlow candidate declares those options;
its `ARCHIVE_TYPE` enum maps 3 to Zstandard binary, although its help text
only describes types through 2. This static comparison cannot establish
runtime compatibility or output correctness.

The private package test now includes generated-cube probes for both exact
command shapes (`scripts/openmvs_odm_cleanup_fixture.py`), in addition to the
previous positive/negative reconstruction and weighted PLY checks. The
hosted trial [43099422521](https://github.com/Archont561/ODM-conda/actions/runs/43099422521)
passed the patched build, package tests and independent retest, including
these command probes and the generated positive/negative reconstruction and
weighted PLY checks. Its private package SHA-256 was
`53f7d1989f60f1b10c2a08e44dc1a11357f6692d285743d9c04b95e9f0c315ce`.
Sources and binaries were discarded. The local fixture unit tests use a stub
executable and test the harness, not OpenMVS.
Neither these probes nor the earlier synthetic scene test run ODM itself.
A full private ODM/Scoped OpenSfM build and end-to-end dataset replay remain
necessary after the patched candidate passes its own tests.

A disposable full-stack attempt using the TetraFlow package instead of the
historical OpenMVS package was started in
[43100369839](https://github.com/Archont561/ODM-conda/actions/runs/43100369839).
It used the reduced runtime and scoped JPEG XL, then a relocated locked replay
and Seneca run. The stack built and replay started, but ODM failed at mesh
cleanup: `ReconstructMesh` required `libjxl.so.0.12`, while the selected JPEG
XL runtime was 0.11. The diagnostic was recovered in
[43106145917](https://github.com/Archont561/ODM-conda/actions/runs/43106145917).
No source, package, dataset or output was uploaded.

The next private recipe build (build 1) explicitly constrains libjxl to
`>=0.11,<0.12` in both host and run environments, matching the scoped plugin.
Package tests check `ldd`, and the new integration trial checks it again in the
relocated full-stack environment before processing data. The repeat
[43106234405](https://github.com/Archont561/ODM-conda/actions/runs/43106234405)
was still running when this note was written; the fix and end-to-end result are
not yet validated. The alternate has source fingerprint and named link-map
checks; the historical OpenMVS audit does not apply to this different package
and is not claimed. These results do not resolve rights or release gates.
