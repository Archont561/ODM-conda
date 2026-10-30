---
id: TASK-63
title: Test OpenSfM asset-reduced runtime in ODM Seneca
status: Done
assignee: []
created_date: '2026-10-29 23:33'
updated_date: '2026-10-30 00:03'
labels:
  - research
  - integration
dependencies: []
ordinal: 63000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Run installed functional and end-to-end tests with the two uncertain vocabularies and SQLite database absent.
- [x] #2 Record changed runtime coverage, fallback behavior, raster metadata and remaining source and license limitations.
- [x] #3 Do not upload research sources, binaries or dataset outputs or change release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Build and audit original research components without modification; in a disposable installed prefix only, verify and remove two vocabularies and the SQLite database, assert fallback behavior, and run the reduced OpenMVS Seneca experiment. This does not create a distributable artifact.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Run 40973960114 removed verified vocabularies and SQLite from installed disposable prefix after normal package tests/audit, confirmed 3708-entry JSON sensor fallback, and completed Seneca fast-orthophoto. Raster 9545 x 10629 RGBA EPSG:32617; recovered metadata via read-only 40977152684. Not a reduced package, rights review or validation of BoW/VLAD/cameras beyond JSON. No sources, binaries or outputs uploaded; gates unchanged.
<!-- SECTION:NOTES:END -->
