---
id: TASK-61
title: Validate reduced OpenMVS in ODM dataset integration
status: Done
assignee: []
created_date: '2026-10-29 22:45'
updated_date: '2026-10-29 23:10'
labels:
  - integration
dependencies: []
ordinal: 61000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Build and retest the reproducibly reduced OpenMVS tree and use it in a disposable nine-component ODM Seneca trial.
- [x] #2 Inspect the final raster metadata when produced and document exact inputs and limitations.
- [x] #3 Keep research sources, packages and dataset outputs private; do not change release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Reuse the hash-verified disposable Seneca pipeline, switching its OpenMVS research build to the reproducibly reduced copy; verify final raster if generated and record success or blocker.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Disposable run 40968370151 passed reduced-copy OpenMVS build, fresh retest, limited audit and nine-component Seneca pipeline; final raster 9667 x 10305 RGBA EPSG:32617 and report metadata inspected. Exact inputs, hashes and limitations recorded in research/odm-fast-orthophoto-prototype.md. No sources, research binaries or dataset outputs uploaded; no release gates changed.
<!-- SECTION:NOTES:END -->
