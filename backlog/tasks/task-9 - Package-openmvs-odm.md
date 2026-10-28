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

Preliminary source research (2026-10-28): ODM SuperBuild uses mutable openMVS branch `355`, resolved to `8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53`; codeload archive SHA256 `949d420d4506ccd0189574252c8214acce666de837e400e44682e8ddc13e666b`. It also selects OpenDroneMap/VCG branch `285` (resolved `3fe55c6fa48ca111dab31eaa594ecab33913a8f1`, archive SHA256 `8f75239f9dd4ee5ba55b0cad25df1b7f9caa8a7e583f8174b40d38421b485f45`) and Eigen commit `7176ae16238ded7fb5ed30a7f5215825b3abd134`. ReconstructMesh's minimal target/dependency closure is not yet established. Archive checksums and complete notices for every enabled source still need review; no recipe or native validation exists.
<!-- SECTION:NOTES:END -->
