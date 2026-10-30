---
id: TASK-80
title: Investigate Seneca dataset rights and raster sanity checks
status: Done
assignee: []
created_date: '2026-10-30 15:38'
updated_date: '2026-10-30 15:52'
labels:
  - research
  - integration
dependencies: []
ordinal: 80000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document immutable dataset license and provenance evidence with unresolved rights
- [x] #2 Implement and test bounded raster sanity checks without claiming geographic validation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Check immutable Seneca repository metadata and add conservative raster sanity tests; do not assert dataset rights.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Pinned Seneca license.txt Git blob 670154e3538863b2d9891fd5483160fbdfc89164 SHA256 36ffd9dc085d529a7e60e1276d73ae5a030b020313e6c5408593a6ae2af39673 is CC0 1.0; README credits Ohio DOT, license added 2019 after 2016 image introduction. Grant authority, privacy and rights not established. Added unit-tested GDAL metadata/statistics sanity checks; generated 16x16 RGB EPSG:32617 GeoTIFF passed. No visual or geographic validation claimed.

Read-only run 41084604140 applied raster sanity checks to logged GDAL metadata for prior 9563 x 10541 Seneca raster. The original raster was not re-opened or retained; visual/geographic accuracy remains unverified.
<!-- SECTION:NOTES:END -->
