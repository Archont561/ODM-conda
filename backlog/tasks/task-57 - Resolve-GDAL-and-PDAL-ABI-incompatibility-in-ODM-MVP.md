---
id: TASK-57
title: Resolve GDAL and PDAL ABI incompatibility in ODM MVP
status: In Progress
assignee: []
created_date: '2026-10-29 11:53'
updated_date: '2026-10-29 15:43'
labels:
  - integration
  - bug
dependencies: []
priority: high
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Disposable integration failed to solve dem2points build 0 with renderdem build 0: the former requires GDAL 3.11 and the latter requires PDAL 2.10, whose available conda-forge builds could not satisfy that GDAL version. Isolated reproduction: https://github.com/Archont561/ODM-conda/actions/runs/40868856018. Determine a common native ABI through versioned, genuinely rebuilt recipes, not by overriding metadata or loosening audits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Select an attainable shared GDAL/PDAL/OpenCV and compiler dependency set, including all MVP package requirements and exact artifact identities.
- [ ] #2 Build and individually retest/audit/source-bundle changed packages with appropriately bumped build versions; retain owner release gates.
- [ ] #3 Install all nine components into a fresh disposable environment, verify imports, binaries and relocation, and continue TASK-13 integration without publishing unapproved artifacts.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a disposable CI solver to identify an attainable GDAL/PDAL/OpenCV runtime baseline; bump and rebuild the affected GDAL-dependent recipes with precise host/run ABI pins, reset changed release gates and keep published historical releases distinct. Validate rendered metadata and fixtures locally, request owner native multi-recipe build, then independently verify artifacts and assemble all nine components for integration. Never relax metadata to conceal ABI incompatibility.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
A disposable conda-forge solve of GDAL 3.13 with PDAL 2.10, Python 3.12, OpenCV 4.12, GDAL Python bindings and the selected integration dependencies failed: https://github.com/Archont561/ODM-conda/actions/runs/40904066709. A GDAL >=3.12,<3.13 solve of the same requested dependency set succeeded: https://github.com/Archont561/ODM-conda/actions/runs/40904165751, selecting libgdal-core 3.12.2 hc2c0581_0, libpdal-core 2.10.0 h9d23c72_0, libopencv 4.12.0 qt6_py312h52d6ec5_612, py-opencv 4.12.0 qt6_py312h598be00_612, Python-PDAL 3.5.3, and TBB 2023.1. This was dependency-only, not the nine actual artifact solve or native ABI proof. Candidate builds of dem2points, fastrasterfilter and odm-orthophoto now target GDAL 3.12 at host and run, bump build 0 to 1 and reset all four release flags. Published build 0 artifacts remain unchanged; dem2mesh stays outside MVP. Local pixi check passed (246 passed, 2 skipped); native dem2points build staged pinned source but failed conda-forge noarch repodata EOF before compilation; no new native package, test, audit or source bundle was produced. Owner must dispatch build.yml with the three changed recipes selected. Full integration solve, actual build/run ABI, legal/source review and owner gates remain open.
<!-- SECTION:NOTES:END -->
