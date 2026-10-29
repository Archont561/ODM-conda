---
id: TASK-13
title: Package the ODM application and validate fast-orthophoto integration (MVP)
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-29 18:28'
labels:
  - component
  - opendronemap
milestone: m-11
dependencies:
  - TASK-3
  - TASK-24
  - TASK-27
  - TASK-29
  - TASK-31
  - TASK-35
  - TASK-37
  - TASK-39
  - TASK-41
  - TASK-43
  - TASK-57
priority: high
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/ODM
Reference in selected ODM build: 47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45
Next work: Package application files/launcher; replace SuperBuild path assumptions and consume validated component packages.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
- [ ] #4 The application consumes packaged components rather than rebuilding SuperBuild; resources, imports, paths and the odm launcher work after relocation.
- [ ] #5 A suitably licensed end-to-end drone dataset succeeds in a fresh environment; unsupported features are explicit.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Develop a local-only fast-orthophoto integration prototype against the hash-pinned ODM source: map context paths to an explicitly supplied Conda prefix, test relocatable paths and launcher preflight, investigate dataset rights, and keep component/legal/end-to-end release prerequisites open.

Attempt local-only assembly and launch prerequisites using existing locked tools and component builds; record exact blockers and possible next steps without packaging or publishing unreviewed research sources.

Use a temporary CI job to build and audit the two research components, assemble a disposable environment with hash-verified existing non-published artifacts and required tools, run preflight and launcher, and only if those pass attempt the pinned CC0-licensed Seneca candidate without uploading outputs. Record first blocker; keep production and legal gates unchanged.

Re-run disposable integration with independently verified coordinated artifacts and locally built research components. Capture the actual nine-component solve and run preflight, selected imports, launcher and candidate dataset only when prerequisites pass; record relocation and all blockers, retain no research or dataset artifacts.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MVP scope (approved, see doc-11): fast-orthophoto path only. Removed gates TASK-33 (dem2mesh, not used by fast mode) and TASK-45 (OpenPointClass, opt-in via --pc-classify). Kept TASK-39, rescoped to the OpenMVS ReconstructMesh target because the 2.5D poisson cleanup calls it. Acceptance #5 is now a fast-orthophoto dataset run. Full-pipeline features (dense OpenMVS, gridded DEM mesh, pc-classify) are explicitly unsupported in this MVP.

2026-10-28 planning checkpoint: native component research evidence and outstanding licensing/readiness gates are summarized in research/component-readiness-review.md and research/open-components-license-review.md. TASK-35, 37, 39, 41 and 43 remain open; no complete ODM integration validation or authorization to bypass prerequisites is implied.

Local-only prototype: inspected pinned ODM source and staged archive SHA256 5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e. Adapter maps ODM paths to an explicit component prefix; verified patched context after moving the source tree. Prefix preflight on odm-dev fails for all nine ODM-specific tools; no combined prefix, genuine binary relocation, launcher execution, dataset run or ABI validation. Candidate Seneca CC0 dataset is 167 images/376 MB, not a verified small fixture; Garfield RGB 28 images/59 MB reportedly fails ODM matching. See research/odm-fast-orthophoto-prototype.md. Production and legal prerequisites remain open.

Restored environment; odm-dev preflight still lacks nine component tools. Local OpenSfM research build verified sources with system CA and applied patch, then failed conda-forge noarch repodata unexpected EOF; no package/prefix/launcher/dataset test. See research/odm-fast-orthophoto-prototype.md.

Disposable runner https://github.com/Archont561/ODM-conda/actions/runs/40866808464 verified seven artifact ZIPs, built research OpenSfM and OpenMVS, passed their packaged and isolated tests and limited audits, but the nine-component install could not solve. https://github.com/Archont561/ODM-conda/actions/runs/40867845237 repeated and exposed GDAL/PDAL conflicts. Minimal two-package reproduction https://github.com/Archont561/ODM-conda/actions/runs/40868856018 shows dem2points requires libgdal-core >=3.11.5,<3.12 while renderdem requires libpdal-core >=2.10,<2.11, with no viable common current conda-forge solve. No combined prefix, preflight, launcher, dataset or relocation test was reached. Research and dataset outputs not uploaded. TASK-57 tracks shared ABI remediation; release gates unchanged.

TASK-57 has a dependency-only candidate solve (GDAL 3.12/PDAL 2.10/OpenCV 4.12); three fast-path GDAL consumers have build-1 candidates and reset release flags. No new artifacts or combined environment exist yet; owner native builds and full integration validation are still required.

TASK-57 independent artifact inspection found that three GDAL build-1 candidates passed individually but still do not solve with historical RenderDEM because actual generated GDAL and PDAL runtime minimums conflict. Four newly coordinated builds are needed before combined-prefix work can continue.

The four GDAL/PDAL-dependent candidate artifacts installed together in a disposable Python 3.12 environment in https://github.com/Archont561/ODM-conda/actions/runs/40910163219; binaries present. This is not the nine-component environment or a launcher/dataset/relocation test. TASK-57 remains open.

Run 40916199152 passed launcher help after adding application dependencies and exposed NumPy 2 incompatibility. After a genuine NumPy 1-compatible OpenSfM rebuild, run 40919353247 reconstructed 166 Seneca images and 198644 points but failed in statistics due to removed matplotlib.cm.get_cmap. Research build 5 constrains Matplotlib and adds installed smoke checks. Full dataset/orthophoto and relocation remain unverified; candidate dataset provenance and all research licensing require review.

Run 40922527022 generated an intermediate orthophoto but crop warned and report failed because PDAL/GDAL could not locate PROJ database. Minimal run 40927345299 reproduced and fixed EPSG:4326 lookup by setting prefix PROJ_DATA or PROJ_LIB; launcher now sets both. Follow-up dataset runs 40927462919 and 40927535532 were canceled; full success, final raster inspection, and full-prefix relocation remain unverified.
<!-- SECTION:NOTES:END -->
