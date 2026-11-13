# ODM Prefix release-readiness inventory

Snapshot: 2026-10-31. Scope: the **linux-64, fast-orthophoto research
candidate**, not complete ODM, NodeODM, GPU support, or every possible feature.
This is a planning inventory, not a legal opinion, approval or source offer.
The authoritative component gates remain in [`recipes/components.json`](../recipes/components.json).

## Current evidence and limits

The owner-dispatched [ODM workflow run 41151384519](https://github.com/Archont561/ODM-conda/actions/runs/41151384519)
passed the private build, relocated locked replay and Seneca integration. The
prior complete source-build [run 41145494232](https://github.com/Archont561/ODM-conda/actions/runs/41145494232)
built 15 local candidates and compared 456 installed Conda identities and
hashes. The application package's rattler-build test was skipped; the installed
launcher, Seneca processing and raster sanity were tested instead. Neither run
proves geographic accuracy, full ODM feature support, distribution rights,
source completeness or bit-for-bit reproducibility. The runs discarded their
bundle and outputs; no durable owner-controlled bundle was retained. See
[TASK-92](../backlog/tasks/task-92%20-%20Make-private-ODM-build-and-lock-replay-repeatable.md)
and the [prototype evidence](odm-fast-orthophoto-prototype.md).

The published components and research candidates are **not interchangeable**:
the tested channel used private identities, including a private OpenCV 4.13
orthophoto variant. Published component approvals apply only to their reviewed
versions and builds. Replacing a research variant with a published package
requires a fresh solve, ABI and integration validation; matching names or
versions alone is insufficient.

## Local package set: 15 candidates

The tested set is assembled by [`private_odm_bundle.py`](../scripts/private_odm_bundle.py)
and its dependencies are declared by the [ODM research recipe](recipes/odm-fast-research/recipe.yaml).
The table is a release-work inventory, not a declaration that a package may be
shipped. Registered components can use the existing component workflow **only
after the exact release candidate meets its gates**; research packages are not
registered release components.

| Candidate | Existing release path and status | Work before ODM distribution |
| --- | --- | --- |
| `odm-fast-research` 3.6.2 | Research-only; no registered release component. | Design a supported release recipe and dependency contract; complete source, license, notice and security review; add package tests and validate the supported application scope. Register only a reviewed release candidate. |
| `fpcfilter` 0.2 | Published build 1; private variant was tested. | If using the published build, validate it in the final stack; otherwise review and release the exact new variant. |
| `dem2points` 0.0.0.dev20220721 | Published build 2; private variant was tested. | Validate the actual release-selected binary with the final stack; a different variant needs its own review. |
| `fastrasterfilter` 1.0 | Published build 2; private variant was tested. | Validate the actual release-selected binary and its obligations in the final stack; a different variant needs its own review. |
| `odm-orthophoto` 0.0.0.dev20250225 | Published build 2 targets a different dependency stack; the tested OpenCV 4.13 variant is private. | Prepare and review a distinct release identity for the chosen ABI or demonstrate the published build works in the final solve. Do not replace immutable published bytes. |
| `renderdem` 1.0 | Registered for component builds; all four release gates false. | Review source and notices, PDAL/GDAL ABI and intended LAS/LAZ coverage; rerun build, tests, audit and source verification on the release candidate. |
| `mvs-texturing-odm` 0.0.0.dev20250818 | Registered; all four gates false. | Resolve MVE and other source/notice rights, including the upstream SIFT/SURF warnings; verify the actual dependency graph, link evidence and complete source. |
| `poissonrecon-odm` 13.8 | Registered; all four gates false. Tested candidate is a reduced research variant. | Decide which production source and build will ship; validate final linkage and security mitigations, bundled JPEG/PNG/zlib provenance, notices and corresponding source. Research audit is not production approval. |
| `opensfm-scoped-odm` 0.5.2 | Reduced research-only package; no registered release component. | Resolve source, license and notice obligations and camera database/vocabulary or other retained-asset rights; confirm reduced scope is fit for the intended supported workflow. |
| `openmvs-odm` 0.0.0.dev20260516 | Reduced research-only package; no registered release component. | Resolve restricted IBFS/TRWS files in the original source archive, selected-code and dependency obligations, notices and a lawful, complete corresponding-source plan. Excluding code from the binary does not clear the original archive. |
| `odm-research-codem` 0.26.1 | Source-built research-only runtime; no registered release component. | Review pinned source, metadata, dependencies and notices; provide release recipe, tests and source plan. |
| `odm-research-pillow-jxl-plugin` 1.3.4 | Source-built research-only runtime; no registered release component. | Review sdist, locked Cargo crates, native library linkage, notices and source obligations; validate the final binary and provide a release recipe/source plan. |
| `odm-research-pygltflib` 1.16.5 | Source-built research-only runtime; no registered release component. | Review pinned source, metadata, dependencies and notices; provide release recipe, tests and source plan. |
| `odm-research-pyodm` 1.5.12 | Source-built research-only runtime; no registered release component. | Review pinned source, metadata, dependencies and notices; provide release recipe, tests and source plan. |
| `odm-research-pysolar` 0.13 | Source-built research-only runtime; no registered release component. | Review pinned source, metadata, dependencies and notices; provide release recipe, tests and source plan. |

`dem2mesh` is registered but unapproved; it is **not** a direct dependency of
the tested fast-orthophoto recipe. Do not add it to this release scope merely
because it is an ODM component. Broader ODM support may require it or further
packages and tests.

A [bounded review of the five Python source inputs and fresh private package
builds](python-research-source-review-2026-11-07.md) identifies additional
license, source and image-rights questions; it does not approve any candidate.

## External runtime and build dependencies

The recipe directly requests Python, PDAL, python-pdal, GDAL, ExifTool,
scikit-image, scikit-learn, Shapely, Fiona, EDT, piexif, trimesh, ONNX Runtime,
packaging and `libopenvino >=2026.0`; their transitive packages and build tools
also matter. These are generally solved from conda-forge, not automatically
packages that this repository must republish to Prefix. Decide the intended
channel order and availability contract, lock the actual release solve and
review its precise dependency/source/notice and compatibility obligations.

The 456-record successful run's lock and complete inventory were discarded.
The retained [sanitized replay inventory](odm-private-lock-replay-inventory.json)
and [earlier combined inventory](odm-combined-conda-inventory.md) describe
**different earlier solves**, not the 456-record release bill of materials.
Create and retain a fresh exact lock and inventory for the proposed release;
do not treat older metadata or binary URLs as a corresponding-source inventory.
The [OpenVINO replay metadata](openvino-2026-2-replay-metadata.json) is bounded
inspection evidence, not complete transitive source or notice clearance.

## Release sequence and decisions

1. **Set scope and freeze candidate:** choose the supported ODM features, package
   identities, exact versions/builds, published-versus-private native variants,
   external channel dependencies and target platform. Retain the exact lock,
   binary hashes, source inputs and inventory in owner-controlled storage.
2. **Resolve blockers per candidate:** perform qualified review of licenses,
   rights, notices, source graphs and security; obtain missing rights or replace
   restricted inputs. Produce and verify corresponding-source bundles for the
   exact distributed artifacts. Do not infer approval from a hash, a scan, or a
   successful private build.
3. **Production packaging and testing:** implement and register release recipes
   for the reviewed candidates, with unique immutable identities and appropriate
   source staging and audit support. Rebuild on the proposed release commit,
   run package/fresh-environment tests, audit and source checks, and validate the
   full resolved stack and intended features. Research-only scope, omitted
   assets and remaining limitations must be explicit.
4. **Owner decision for each exact candidate:** review and commit all four
   component gates: `publishable`, `license_reviewed`,
   `source_completeness_reviewed`, and `native_validation_passed`. Previous
   component approvals do not approve a new variant or the full ODM stack.
5. **Separate publication authorization:** merge reviewed changes, create the
   exact registered component/version/build tag at trusted default-branch HEAD,
   and publish the matching non-draft, non-prerelease GitHub Release. The
   [protected workflow](../.github/workflows/release.yml) rebuilds and audits,
   verifies the release set, attaches source before uploading one binary with
   Prefix OIDC and attestation. It currently supports one registered component
   per release, not the 15-package research bundle. Owner approval of the
   protected `prefix` environment and authorization to publish remain separate.

See the [publishing guide](../backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md),
[component readiness review](component-readiness-review.md),
[Open component review](open-components-license-review.md),
[Poisson review](poissonrecon-readiness-review.md), and
[texturing review](mvs-texturing-license-review.md) for detailed evidence and
unresolved questions. No release gates are changed by this inventory.

## Proposed scope and source-rights decisions (2026-10-31)

For planning, use the already-tested **linux-64 CPU fast-orthophoto** path,
with the 15 candidate package families above and the external conda-forge
stack. This is a proposed minimum scope, not an owner approval or a promise
of full ODM functionality. The exact package builds and external dependency
versions are not frozen until an owner-controlled bundle and lock are created
and reviewed. The Seneca processing result is technical evidence only; it is
not rights clearance or proof of geographic accuracy.

The private bundle builder now retains a `conda-inventory.json` alongside its
manifest, lock and channel, covered by the bundle manifest. A relocated replay
compares installed identity, version, build, SHA256 and sanitized binary URL
against that inventory. Previous schema-1 bundles without an inventory remain
replayable but do not receive this additional comparison. Inventory metadata
is not proof of installed file bytes, complete source, distribution rights, or
legal obligations. Run the documented build on owner-controlled storage to
actually retain the lock, inventory and private binaries; the automated GitHub
workflow intentionally discards them. The TetraFlow variant completed another hosted build and relocated replay in
[43329779932](https://github.com/Archont561/ODM-conda/actions/runs/43329779932);
that runner discarded its private bundle and retained only
[bounded trial identity metadata](odm-tetraflow-private-trial-identities.json).
It is not an owner-retained lock or a release approval.

| Decision | Evidence established | Still needed before release |
| --- | --- | --- |
| OpenMVS restricted original archive | A fingerprinted local reduced tree builds and tests without named IBFS/TRWS inputs; the original archive remains required by the current preparation. See [reduced-tree experiment](open-components-license-review.md#reproducible-local-only-reduced-tree-2026-10-29). | A qualified reviewer and, where necessary, rights holders must determine whether the exact original inputs and/or a reduced source distribution may be used and shared, on what terms. If not, select a legally usable alternative and rebuild/revalidate. The reproducible transformation does not itself grant permission. |
| OpenMVS corresponding source and dependencies | Candidate transformation records retained paths and hashes; build/link and notice evidence are bounded. | Decide the exact distributable source set, obtain its required permissions, verify all patches, build instructions, Boost/CGAL/VCG/Eigen and other required inputs and notices, and test reconstruction from that set. |
| OpenSfM source and assets | The local scoped candidate removes specified pinned assets and uses runtime guards. | Determine rights for the actual retained code, data and dependencies, including sensor database provenance and vmem terms; confirm the stripped assets are genuinely absent from the final distributed set and that reduced scope meets the product requirements. Removing uncertain assets does not clear remaining material. |
| OpenSfM corresponding source | Original archive, candidate transformation and some dependency inputs are pinned; the research candidate explicitly is not a source offer. | Review the exact source graph, additional sources, modifications, scripts, runtime guard, build and packaging instructions and required notices; verify a complete, lawful source offer for the actual release binary. |
| Final stack | Independent research builds and a combined fast-orthophoto trial succeeded. | Freeze the actual release packages and external versions, validate together, and obtain explicit owner approval of each exact candidate's four gates. Existing released component approvals are not approvals of the research variants. |

No rights-holder permission, qualified legal conclusion, source-completeness
attestation or publication approval is implied by these technical steps. The
owner must choose how to obtain a durable private destination and independent
manifest-hash record; GitHub's public repository and research workflow are not
suitable storage for the restricted private bundle.

## Exact published components in a TetraFlow research stack

Hosted trial [43447876789](https://github.com/Archont561/ODM-conda/actions/runs/43447876789)
substituted the three already-published release binaries for the private
rebuilds of fpcfilter, dem2points and fastrasterfilter. They were fetched from
their GitHub Releases and verified against the previously recorded published
SHA256 values; the trial did **not** fetch them from the live Prefix channel.
A distinct private ODM package identity pinned their exact build strings, and
its isolated package test, 432-record relocated locked replay, JPEG XL check,
Seneca fast-orthophoto pipeline and raster sanity passed. Installation metadata
in the replay was checked against the original solve and the three selected
binary SHA256 values. Bounded metadata is in
[`odm-published-component-integration.json`](odm-published-component-integration.json).

This is evidence for those three exact binaries **within that one ephemeral,
modified research stack**. It is not a final release solve, broad functional or
accuracy validation, proof of installed file bytes, source or rights review, or
a new approval of the other components. The published orthophoto was not tested
here; this trial continued using the private OpenCV 4.13 orthophoto variant.
The lock, binaries, data and outputs were discarded. The printed lock and
inventory hashes cannot substitute for retaining those files, and the work
needed before publication above remains open.

## Published orthophoto compatibility with the TetraFlow stack

The exact published orthophoto build 2 binary was fetched from its GitHub
Release (not a live Prefix download), independently matched to SHA256
`c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614`,
and passed its own fresh `rattler-build test` in
[43456421499](https://github.com/Archont561/ODM-conda/actions/runs/43456421499).
Its package index declares both `libopencv >=4.12,<4.13` and
`libopencv >=4.12.0,<4.12.1.0a0`. A separate Pixi solve combining this exact
local binary with `libopencv >=4.13,<4.14` failed; the latter constraint is
required by the current TetraFlow research recipe. This confirms a dependency
conflict for that selected stack; it does not establish that every possible
alternative ODM configuration is incompatible. No full TetraFlow integration
with the published orthophoto ran, and the artifact was discarded.

Two earlier diagnostic attempts failed before testing: the first used an
incorrectly transcribed expected SHA256 and stopped at the checksum guard; the
second matched the correct SHA but assumed one OpenCV constraint and stopped
when the package declared two. The successful probe preserves both constraints.
Do not loosen them or overwrite the published artifact. A distinct OpenCV 4.13
orthophoto build has been used privately, but needs its own production recipe,
unique identity, reviews, release-gate decisions and final-stack validation
before publication. Evidence is recorded in
[`odm-published-orthophoto-compatibility.json`](odm-published-orthophoto-compatibility.json).

### Staged OpenCV 4.13 orthophoto candidate

`scripts/prepare_orthophoto_opencv413_candidate.py --destination /private/new-stage`
creates a disposable copy outside the repository. It preserves the published b2
recipe and manifest, changes the copy's host and run constraints to OpenCV 4.13,
uses build number 3 with the distinct `candidate_opencv413_<hash>_3` string,
and closes **all** orthophoto release checks in the staged manifest. A future
production identity must be separately decided and checked for uniqueness before
publication. This is not an addition to the release workflow.

[Hosted run 43457662447](https://github.com/Archont561/ODM-conda/actions/runs/43457662447)
built that candidate, ran the recipe's functional tests, retested the package
in a fresh environment, and passed the existing artifact audit against the staged
manifest. Bounded metadata is in
[`odm-orthophoto-opencv413-candidate-evidence.json`](odm-orthophoto-opencv413-candidate-evidence.json).
The executable directly needs OpenCV `.so.413`; runtime metadata restricts
OpenCV to 4.13.0. The candidate artifact was discarded and its hash identifies
only that trial, not a reproducible or retained release artifact.

The staged package's SOURCE.txt points to the *prospective* build 3 release
source URL; the audit checks the URL's format/identity, not that the source
bundle exists there. A matching source bundle, complete dependency and rights
review, owner-controlled gates, a retained final candidate and full final-stack
solve/replay/Seneca test remain necessary. Previous research-stack integration
used a different `research_*_2` binary, not this candidate's bytes. Never
publish this staged candidate merely because its artifact audit passed.
