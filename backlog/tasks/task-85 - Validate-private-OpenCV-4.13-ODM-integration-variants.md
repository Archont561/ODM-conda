---
id: TASK-85
title: Validate private OpenCV 4.13 ODM integration variants
status: In Progress
assignee: []
created_date: '2026-10-30 17:54'
updated_date: '2026-10-30 18:17'
labels:
  - research
  - integration
dependencies: []
ordinal: 85000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify nine-component OpenCV ABI dependencies and prepare isolated research variants without weakening production checks
- [ ] #2 Build and fresh-test affected variants with existing audits or record concrete blockers
- [ ] #3 Attempt combined OpenVINO 2026 integration and Seneca raster validation if the solve and builds succeed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Trace exact ABI requirements, stage temporary private recipe variants targeting OpenCV 4.13, retain existing checks, rebuild and retest affected components, then solve and run Seneca if possible; document limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Three direct OpenCV recipe consumers identified: orthophoto, scoped OpenSfM and reduced OpenMVS; other six recipe inputs do not directly name OpenCV but transitive/ABI compatibility is unverified. Added tested private copy preparer. Native private run 41102357808 has an assigned GitHub Actions runner but no started steps after more than 20 minutes; outcome unknown. Cancellation attempt denied HTTP 403. Local pixi conda-forge solve failed TLS handshake EOF. Build, fresh tests/audits and integration remain open.
<!-- SECTION:NOTES:END -->
