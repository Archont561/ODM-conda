---
id: TASK-6
title: Package dem2mesh
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 10:37'
labels:
  - component
  - dem2mesh
milestone: m-4
dependencies: []
priority: medium
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/dem2mesh
Reference in selected ODM build: 334
Next work: Carry the selected ODM release patches and audit JMeshLib.
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
Owner selected the six-component bulk scope on 2026-10-28, explicitly including dem2mesh before the fast-orthophoto MVP ships. It remains outside the TASK-13 fast-path dependency gate.

Preliminary source research (2026-10-28): ODM 3.6.2 SuperBuild uses `GIT_TAG 334`, a mutable branch, whose head resolved to `623c8536941175c630fabe4f1352ddc314d98120`. Its codeload archive SHA256 is `29e2729c890118def3d727cfca81070e1cb99fa8a51212a6deef7614089ecf8b`. The inline SuperBuild definition specifies no patch command for this component. The archive vendors JMeshLib and builds it statically; its README and headers state GPL version 2 or later, while its bundled gpl.txt contains GPL v2. Review all compiled files and compatibility with the root GPL grant before deciding metadata and notices. The source graph and notices are not yet fully reviewed; no recipe or native validation exists.

Research-only build and scene (2026-10-28): staged the pinned dem2mesh archive after hash verification, configured against restored odm-dev GDAL 3.12.2 with system GCC 12 and CMake, and built the bundled static JMeshLib plus dem2mesh. The first link failed due to older system libstdc++; explicitly adding odm-dev lib and rpath-link allowed it to link. A generated 8x8 Float32 GeoTIFF with elevation x+y, processed with maxConcurrency 1 and maxVertexCount 1000, returned success and produced a binary little-endian PLY with 64 vertices and 98 faces. This is an unisolated research binary with manually mixed toolchain and GDAL version, not a production recipe, ABI validation, installed-prefix functional test or native CI evidence. JMeshLib grant and full notices remain to be reviewed and approved separately.
<!-- SECTION:NOTES:END -->
