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
