---
id: TASK-4
title: Package odm-orthophoto
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 20:05'
labels:
  - component
  - odm-orthophoto
milestone: m-2
dependencies: []
priority: medium
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/odm_orthophoto
Reference in selected ODM build: 355
Next work: Port CMake recipe, GDAL/OpenCV dependencies, licenses, and an orthophoto fixture.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-27: implementation landed. Reference resolution: ODM 3.6.2's SuperBuild CMakeLists.txt (commit 47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45) pins odm_orthophoto inline with `GIT_TAG 355`; the upstream repository has no tags and uses numbered branches — `git ls-remote` confirmed `refs/heads/355` at commit `55b66d87cc168b8ab287bf10e81d4da0890f84f1` ("GDAL texture read fallback", committed 2025-02-25). That commit is pinned; upstream `main` (6a7e81b, newer) is deliberately not used. The codeload archive was fetched and hashed: SHA256 `a3f3410b85504898c788eb2be096c1153e9ac58d4a6139a5d3087d92f5b528d2` (26,023 bytes). SuperBuild applies no patch to odm_orthophoto (only ceres.patch/pdal.patch exist), so AC #1's patch review resolves to "none required"; the archive has no `.gitmodules` and its CMakeLists contains no ExternalProject/FetchContent/file(DOWNLOAD). License: LICENSE is full AGPL-3.0 text, source files carry no separate headers, no or-later grant, and no vendored third-party code (src/ = Logger, OdmOrthoPhoto, main only) → conservative `AGPL-3.0-only AND MIT` pending owner review (doc-6 inventory entry added; AGPL §13 network clause flagged). Version: upstream declares none (`project(odm_orthophoto)` without VERSION) → snapshot `0.0.0.dev20250225` from the pinned commit date per the dem2points precedent. Dependencies from upstream CMake: GDAL, Eigen3, OpenMP, OpenCV (core/imgproc/highgui/photo), C++17, stdc++fs → recipe pins `libgdal-core >=3.11,<3.12` (matches dem2points), `eigen >=3.4,<4` (Ubuntu 24.04 generation used by ODM 3.6.2), `libgomp >=14` (fpcfilter precedent), `libopencv >=4.12,<4.13` (the project-wide OpenCV choice recorded in pixi.toml odm-dev). The installed-prefix fixture (scripts/functional_test.py) generates a 4x4 solid-red PNG texture, MTL and a 2 m x 2 m textured quad OBJ, runs the binary with `-resolution 2 -outputDepthIdx 0` (`-outputDepthIdx` is mandatory: without it upstream never probes the texture depth and exits 1 with "Unsupported bit depth value: -1"), and verifies in pure Python — no GDAL bindings, network or sample data — the corner-bounds file (100 200 102 202), the GeoTIFF IFD (4x4, RGBA 8-bit, contiguous, uncompressed strips) and the exact pixel bytes (0,0,255,255: band i holds cv::imread channel i, BGR, with alpha last; texture coordinates are inset 0.25–0.75 so upstream's bilinear (left+1, top+1) reads stay in bounds). Machinery generalized in the same change: audit_package required-runtime map (libgdal-core+libgomp+libopencv), build.py help, build.yml dispatch options, functional_test dispatch/executable mapping, test_helpers expectations (3 recipes). NOT yet done: native build/reinstall-test/audit/sources runs — these need an owner-dispatched build.yml run in CI (this sandbox cannot build natively or dispatch workflows), so AC #2's installed-prefix pass is not yet demonstrated, all four release gates remain `false`, and this task stays To Do. Next: owner dispatches build.yml (component=odm-orthophoto), then evidence review as TASK-28.
<!-- SECTION:NOTES:END -->
