---
id: TASK-11
title: Package renderdem
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - renderdem
milestone: m-9
dependencies: []
priority: medium
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/RenderDEM
Reference in selected ODM build: main
Next work: Resolve immutable revision and test its PDAL-based DEM renderer.
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
Preliminary source research (2026-10-28): ODM SuperBuild uses mutable RenderDEM `main`, resolved to `93502f2e225be0cebcb8663db3bc5058baa3eb1e`; codeload archive SHA256 `748cb2839db7d24ee3fdce034e8637829630a9d68ec6561fb76523e25d24af8d`. Upstream CMake declares project version 1.0, uses PDAL and OpenMP and installs `renderdem`; the archive includes cxxopts and an AGPL v3 root license. ODM pins PDAL at `831631084edc7e61bc898eae136294c375b13d14` (project version 2.9.0) and applies `pdal.patch` to export private GDALGrid methods. The selected RenderDEM commit instead uses the public PDAL GDAL writer; compatibility with a separately packaged conda-forge PDAL remains to be tested, not assumed. Owner license review, a functional raster fixture and native validation remain open; no recipe exists.
<!-- SECTION:NOTES:END -->
