---
id: TASK-9
title: Package openmvs-odm (ReconstructMesh target for the fast-orthophoto MVP)
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 19:08'
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

2026-10-28: research ReconstructMesh successfully reconstructed the pinned upstream apps/Tests/data/scene.mvs sparse point cloud (2,663 points and four calibrated images) into a validated binary PLY with 1,696 vertices and 3,354 faces, using --archive-type 1 --min-point-distance 0 and disabled mesh cleanup in a temporary directory. scripts/openmvs_pointcloud_fixture.py verifies the exact five upstream input hashes, checks reconstruction output structure and indices, and includes negative tests. Test data remains in upstream source and its licensing/redistribution has not been reviewed. This is a system-GCC/restored-Pixi mixed research build, not an installed-prefix Conda package test, a dense point-cloud pipeline test, a separate PLY point-cloud input test, or an ABI/CPU/source/license audit. An initial default-archive invocation attempted to load a nonexistent same-name PLY; --archive-type 1 correctly used the point cloud in the scene.

2026-10-28: re-staged OpenMVS, VCG and exact ODM Eigen commit; built ReconstructMesh with system GCC 12, the pinned Eigen headers, restored odm-dev libraries, optional CUDA/OpenGL/Breakpad/tests off, and CMake switches disabling SSE3/SSSE3/SSE4/AVX plus -march=x86-64 -mno-popcnt. Compile commands for SceneReconstruct and ReconstructMesh included pinned Eigen, omitted those higher-ISA flags and used the requested baseline. Local research fixtures passed (generated cube cleaning and 2663-point scene reconstruction). This is a mixed-environment research build, not a complete instruction or shared-library baseline audit or a Conda artifact. Separate plain and scalar-views PLY inputs crashed upstream; TASK-53 tracks experimental fix and installed-package validation.

2026-10-28 preliminary notice triage: Ninja dependency output for the local baseline ReconstructMesh configuration listed 137 unique OpenMVS source/header paths, 118 VCG paths and 251 paths from the staged pinned Eigen installation. A basic textual scan is not a full license inventory: 117 VCG paths include GPL version 2 or later header wording; VCG root LICENSE.txt is GPL v3 text (SHA256 589ed823e9a84c56feb95ac58e7cf384626b9cbf4fda2a907bc36e103de1bad2), while vcg/complex/complex.h has an explicit GPL-2.0-or-later grant (SHA256 4bbd5e7404c4ac1488c4d94203e321ea11bec011e4c7a645eabac1446c3459a3). OpenMVS libs/IO/tiny_gltf.h (SHA256 8b1b2fd626a8fcd562741327acaaaabf14032f74bf02d614bce97a436a093e03) contains MIT and embedded other notices including a Boost Software License reference. Pinned Eigen contains multiple COPYING files and observed COLAMD/BSD notice-bearing paths. Do not infer a final SPDX expression or owner approval from these preliminary observations; full per-file, dependency and corresponding-source review remains open.

2026-10-28: experimental OpenMVS source bundle verified all three pinned archives and includes the visibility research patch; SHA256 d67e7ac854bcc0f7a851aecb42a15c5dd483b41ae62e939e7995ebc0a92957e5. This is still the research bundler, not the production corresponding-source bundle; it does not establish license/source completeness or support release.

Generated an independent synthetic MVSI v3 scene with two cameras, generated PNGs and 400 visible points; the patched local research executable reconstructed 53 vertices/46 faces, and rejected both separate no-camera-ID PLY variants cleanly. This avoids relying on unreviewed upstream test imagery, but has not run in an installed package. Offline check passed 133 Python tests. Production multi-source staging, recipe, notices, package tests and native CI remain incomplete.

2026-10-28: detected IBFS research-only license in the original binary and TRWS non-commercial license in SceneDensify source. Experimental openmvs-reconstruct-only.patch (SHA256 2dc920d550119443bb8d079911b0cdfc4cc747eb916a48a01e09ebdaf6a2c96a) selects upstream Boost graph-cut instead of IBFS and excludes dense/refine/texture source files and IBFS/TRWS Math build/install entries. GCC 12 local reduced target built and passed synthetic 400-point reconstruction (53 vertices/46 faces), upstream 2663-point research fixture (1696 vertices/3354 faces), cube mesh cleaning, and two clean visibility errors. nm found no IBFS or MRFEnergy symbols; Math archive and MVS archive exclude IBFS, dense/refine/texture objects, except CUDA-disabled SceneRefineCUDA.cpp.o. This is a research build, not a complete binary or legal audit; source archives still contain restricted files. TASK-54 tracks required review. The patch intentionally supports ReconstructMesh only and is not a full OpenMVS build.

2026-10-28: production source_bundle.py now recognizes only the exact researched OpenMVS, VCG and Eigen archive graph, stages it in a temporary tree, verifies all archive hashes again during bundling, rejects unrecognized graph modifications and scans each archive for CMake fetches. For the pinned Eigen archive only, its lapack tree is excluded from static scanning because this reduced build uses headers; the original archive remains in the bundle. Local cached three-archive graph verified; tests cover full bundled contents, a tampered archive, graph mutations and active fetch outside the Eigen exception. This does not prove no network access, license/source completeness or release readiness. Recipe, lint and builder still reject the graph until the remaining integration is complete.

The installed-test entry point now invokes the generated OpenMVS reconstruction and invalid-visibility fixtures from copied package helper scripts, and rejects missing output. Tested using an artificial prefix populated with the local reduced research executable and restored runtime libraries; this is NOT a Conda installed-prefix, relocation, ABI or native CI validation. The production build guard still rejects OpenMVS until a supported recipe and graph-aware builder are implemented. Also hardened static archive fetch scanning to normalize tabs as well as spaces/newlines.

2026-10-28: implemented a fail-closed builder branch for the exact three-archive OpenMVS graph. It requires both exact patch metadata and a SHA256 fingerprint over 3297 staged file names/contents after the two patches (fe27f5deb6774cd3204f8c70914a7e9fa05c7fb4ac4e1c37d7fe782658c4c668); symlinks, special files and changes are rejected. The branch configures Eigen headers and VCG, disables nonbaseline SIMD options and optional integrations, builds only ReconstructMesh, and copies only that executable and test/provenance files. Re-staged archives, applied patches, and built 47/47 targets using system GCC 12 and symlinked Pixi dependencies into an artificial host prefix; the generated installed-layout fixture passed. This is not isolated rattler/Conda, no-network, binary/ABI or legal validation. Lint still rejects the graph until recipe integration; no recipe or workflow checkbox yet.

2026-10-28: enabled -DEIGEN_MPL2_ONLY in the reduced build to enforce the upstream Eigen COPYING.README selection; GCC 12 research rebuild completed 47/47 and synthetic reconstruction plus both visibility rejection tests passed. This does not replace review of the Eigen notice-bearing files or external dependencies. research/openmvs-notices.json tracks 499 exact file hashes from the reduced build and license evidence; it is not a final legal inventory.

Source archive scanning now uses a single exact hashed Eigen lapack/CMakeLists.txt exception instead of excluding its whole lapack subtree; unrecognized fetch commands elsewhere remain rejected. No new claim of network isolation or license approval.

2026-10-28: added experimental local-only reduced OpenMVS ReconstructMesh research recipe and isolated build/test runner; it is not registered as a production component and native Conda build has not run. Owner-dispatched research workflow retains no package or source artifact and performs fresh retest and a bounded leak/RPATH audit. Upstream archive contains restricted IBFS/TRWS material; no distribution or license approval is implied.
<!-- SECTION:NOTES:END -->
