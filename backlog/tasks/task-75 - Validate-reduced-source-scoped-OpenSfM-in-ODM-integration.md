---
id: TASK-75
title: Validate reduced-source scoped OpenSfM in ODM integration
status: Done
assignee: []
created_date: '2026-10-30 14:21'
updated_date: '2026-10-30 15:12'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 75000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Build and audit reduced-source scoped OpenSfM privately
- [x] #2 Install current MVP packages and run Seneca pipeline with scoped package
- [x] #3 Record outputs and limitations without retaining artifacts
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a private workflow to build and audit reduced-source scoped OpenSfM and run the Seneca pipeline with current research packages.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Prepared a private Seneca integration workflow using the actual reduced-source scoped OpenSfM and Poisson research variants, but GitHub TLS handshakes failed before push/dispatch; no new native build or dataset trial ran. Prior run 40980893166 used earlier scoped package, not this reduced-source build.

Private run 41072814562 built and audited reduced-source scoped OpenSfM (package SHA e1ab0126083e77abd922970718e347b0b641264d67161008489df5e3e287dc30), installed nine actual packages and completed Seneca. Raster 9563x10541 RGBA Byte EPSG:32617; 112964268 bytes; report 7327735 bytes. Bounded metadata independently recovered from log in 41078491919. All outputs discarded; dataset rights and visual/geographic validation remain open.
<!-- SECTION:NOTES:END -->
