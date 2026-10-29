---
id: TASK-57
title: Resolve GDAL and PDAL ABI incompatibility in ODM MVP
status: In Progress
assignee: []
created_date: '2026-10-29 11:53'
updated_date: '2026-10-29 15:40'
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
