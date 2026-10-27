---
id: TASK-9
title: Package openmvs-odm (ReconstructMesh target for the fast-orthophoto MVP)
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 08:38'
labels:
  - component
  - openmvs-odm
milestone: m-7
dependencies: []
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/openMVS
Reference in selected ODM build: 355
MVP scope (approved, see doc-11): ODM's fast-orthophoto path calls only the ReconstructMesh tool from OpenMVS (cleanup in the PoissonRecon meshing path). DensifyPointCloud and the dense stage are not required for the MVP. Confirm the minimal target set against the pinned sources before choosing the build.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
- [ ] #4 Confirm which OpenMVS CMake targets ReconstructMesh needs at ODM 3.6.2 reference 355 (no DensifyPointCloud), and whether it can be built without the full dense dependency tree. Record the result in the task notes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Scope reduced to ReconstructMesh for the MVP. Full OpenMVS dense build is deferred. Acceptance #1 and #2 below apply to the reduced target.
<!-- SECTION:NOTES:END -->
