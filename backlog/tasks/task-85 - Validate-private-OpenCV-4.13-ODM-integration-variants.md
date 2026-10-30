---
id: TASK-85
title: Validate private OpenCV 4.13 ODM integration variants
status: Done
assignee: []
created_date: '2026-10-30 17:54'
updated_date: '2026-10-30 18:32'
labels:
  - research
  - integration
dependencies: []
ordinal: 85000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify nine-component OpenCV ABI dependencies and prepare isolated research variants without weakening production checks
- [x] #2 Build and fresh-test affected variants with existing audits or record concrete blockers
- [x] #3 Attempt combined OpenVINO 2026 integration and Seneca raster validation if the solve and builds succeed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Trace exact ABI requirements, stage temporary private recipe variants targeting OpenCV 4.13, retain existing checks, rebuild and retest affected components, then solve and run Seneca if possible; document limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Three direct OpenCV recipe consumers identified: orthophoto, scoped OpenSfM and reduced OpenMVS; other six recipe inputs do not directly name OpenCV but transitive/ABI compatibility is unverified. Added tested private copy preparer. Native private run 41102357808 has an assigned GitHub Actions runner but no started steps after more than 20 minutes; outcome unknown. Cancellation attempt denied HTTP 403. Local pixi conda-forge solve failed TLS handshake EOF. Build, fresh tests/audits and integration remain open.

Correction: GitHub job details had been incomplete; private run 41102357808 completed successfully. The three OpenCV 4.13 copies and reduced Poisson built, passed fresh tests and respective audits; nine packages solved with OpenVINO >=2026.0; preflight, Seneca and live GDAL raster sanity passed (9508 x 10599 EPSG:32617). 424 Conda records, no missing license metadata fields, nine missing local SHA256 metadata. Exact OpenVINO version/full transitive inventory not retained. No release, complete rights or visual/geographic accuracy established. The run implemented equivalent temporary recipe edits, not the subsequently added preparer.
<!-- SECTION:NOTES:END -->
