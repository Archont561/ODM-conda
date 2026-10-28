---
id: TASK-9
title: Package openmvs-odm (ReconstructMesh target for the fast-orthophoto MVP)
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 13:46'
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

Staging research (2026-10-28): a provisional graph stages the primary archive, VCG and an Eigen GitHub mirror archive of commit `7176ae16238ded7fb5ed30a7f5215825b3abd134` (mirror archive SHA256 `a14492af4d1451a686caadbfd5047ca1216b8c66e71f0e8385afc4bb3ecdc7a3`) into a fresh local tree. `_external` paths require explicit build configuration. This smoke test does not establish GitLab archive equivalence, target closure, network-free build behavior, notices or source completeness.

Eigen review (2026-10-28): the GitLab API confirms that ODM's GitLab commit `7176ae16238ded7fb5ed30a7f5215825b3abd134` exists; GitHub's mirror resolves the same Git commit to tree `72916b38553c81462f2148f8a4119830830987aa`. GitLab's listed `Eigen` subtree `8ef8d3f66401215e00c9d42a80d64e4038ce0d1a` agrees with that GitHub tree. This verifies Git object identity, not equality of GitLab/GitHub tarball bytes, license coverage or target closure. GitLab API: `https://gitlab.com/api/v4/projects/libeigen%2Feigen/repository/commits/7176ae16238ded7fb5ed30a7f5215825b3abd134` and `/repository/tree?ref=7176ae16238ded7fb5ed30a7f5215825b3abd134&per_page=100`.

Source-target inspection (2026-10-28): apps/ReconstructMesh/CMakeLists.txt links the MVS target; libs/MVS/CMakeLists.txt requires CGAL and VCG and links Common, Math and IO. That library globs all its C++ sources, so a ReconstructMesh-only executable target does not itself eliminate dense-source compilation. CUDA, OpenGL and Breakpad can be disabled; default build/Utils.cmake enables SSE3, SSSE3, SSE4.1 and SSE4.2 on x86_64, requiring baseline review. A local configuration attempt with those optional integrations disabled stopped at missing Boost components; CGAL is also absent from the restored odm-dev environment. The closure has not been compile-validated, and no recipe or installed test exists.

2026-10-28: The pinned openMVS Git commit was fetched into a temporary local bare Git repository and scripts/verify_gitlinks.py verified the primary tree contains no Git submodule links. The separately staged VCG/Eigen dependencies are still necessary and this does not prove source completeness or isolated package support.

2026-10-28: pixi-sandbox relock bot resolved cgal-cpp 6.1.1, libboost-devel 1.88.0 and tbb-devel 2023.1.0 into the odm-dev development environment; published sandbox snapshot was refreshed and restored locally. With the staged OpenMVS and VCG archives, system GCC 12, restored odm-dev Boost/Eigen 3.4/OpenCV/CGAL and CMake 4, configured with CUDA, Breakpad and tests disabled and built the ReconstructMesh target with -j1. The executable printed --help (exit 1). It compiled the full MVS library including SceneDensify and SceneRefine; this does not prove a reduced dense dependency closure. This is a mixed local research build, not a Conda package, installed-prefix functional test, isolated build or license/ABI/CPU-baseline audit. The pinned external Eigen tree was staged but this configuration selected the environment Eigen; CPU feature flags require review. All release gates remain open.

2026-10-28: the locally built mixed-environment ReconstructMesh processed a generated eight-vertex, twelve-triangle PLY cube with decimation 0.9; the resulting binary PLY contained seven vertices and ten valid faces. scripts/openmvs_fixture.py reproduces the mesh import/cleaning test and validates mesh structure and indices; negative tests reject missing/truncated/invalid output. This is not point-cloud reconstruction, an installed-prefix test, an isolated Conda build, or CPU/ABI/license validation. The current experimental executable uses system GCC 12 and the restored odm-dev dependencies and may enable nonbaseline CPU flags.
<!-- SECTION:NOTES:END -->
