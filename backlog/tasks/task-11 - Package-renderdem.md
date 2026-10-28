---
id: TASK-11
title: Package renderdem
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 10:56'
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

2026-10-28: added a linux-64 recipe pinned to the researched RenderDEM main commit and provisional AGPL-3.0-only AND MIT metadata, with all four release gates false. Staged source hash matched. Local research compilation succeeded against odm-dev PDAL 2.10.0 and system GCC 12 using a manually mixed toolchain; the selected upstream source uses PDAL public writers.gdal rather than the private GDALGrid API requiring ODM patch. Generated 65x65 constant-elevation PLY produced a 65x65 Float32 GeoTIFF containing exactly 42 at every pixel; scripts/functional_test.py checks the raster and geotransform. This fixture covers PLY input, not LAS/LAZ. Recipe renders and a hash-verified source bundle was assembled. A native rattler build attempted to resolve GCC 14 dependencies but conda.anaconda.org was unreachable; no Conda artifact, installed-package test, isolated build, artifact audit, full source and notice review, or owner license approval exists yet. PDAL 2.10 compatibility and transitive plugin availability in the eventual installed package require native validation.

The generated fixture was extended to also synthesize an uncompressed LAS 1.2 grid with classification 2; both LAS (PDAL reader and classification filter) and PLY paths produced the same expected raster with the local research binary. LAZ remains untested. Installed-prefix/native CI validation is still outstanding.
<!-- SECTION:NOTES:END -->
