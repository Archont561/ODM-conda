---
id: TASK-13
title: Package the ODM application and validate fast-orthophoto integration (MVP)
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-29 11:19'
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
Attempt local-only assembly and launch prerequisites using existing locked tools and component builds; record exact blockers and possible next steps without packaging or publishing unreviewed research sources.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MVP scope (approved, see doc-11): fast-orthophoto path only. Removed gates TASK-33 (dem2mesh, not used by fast mode) and TASK-45 (OpenPointClass, opt-in via --pc-classify). Kept TASK-39, rescoped to the OpenMVS ReconstructMesh target because the 2.5D poisson cleanup calls it. Acceptance #5 is now a fast-orthophoto dataset run. Full-pipeline features (dense OpenMVS, gridded DEM mesh, pc-classify) are explicitly unsupported in this MVP.

2026-10-28 planning checkpoint: native component research evidence and outstanding licensing/readiness gates are summarized in research/component-readiness-review.md and research/open-components-license-review.md. TASK-35, 37, 39, 41 and 43 remain open; no complete ODM integration validation or authorization to bypass prerequisites is implied.

Local-only prototype: inspected pinned ODM source and staged archive SHA256 5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e. Adapter maps ODM paths to an explicit component prefix; verified patched context after moving the source tree. Prefix preflight on odm-dev fails for all nine ODM-specific tools; no combined prefix, genuine binary relocation, launcher execution, dataset run or ABI validation. Candidate Seneca CC0 dataset is 167 images/376 MB, not a verified small fixture; Garfield RGB 28 images/59 MB reportedly fails ODM matching. See research/odm-fast-orthophoto-prototype.md. Production and legal prerequisites remain open.
<!-- SECTION:NOTES:END -->
