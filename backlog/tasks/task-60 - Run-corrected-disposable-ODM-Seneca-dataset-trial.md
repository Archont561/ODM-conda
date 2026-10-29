---
id: TASK-60
title: Run corrected disposable ODM Seneca dataset trial
status: In Progress
assignee: []
created_date: '2026-10-29 21:41'
updated_date: '2026-10-29 21:41'
labels:
  - integration
dependencies: []
ordinal: 60000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Assemble published components and local-only research components in a disposable Linux prefix and run corrected ODM fast-orthophoto on the pinned Seneca dataset.
- [ ] #2 If the workflow completes, independently inspect final GeoTIFF dimensions, coordinate system, geotransform, bands and statistics; otherwise record exact blocker without claiming success.
- [ ] #3 Record package identities, run evidence and limits; do not upload research components or dataset outputs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a temporary restricted GitHub Actions workflow to obtain and verify published and research-only inputs, rebuild and retest OpenSfM and OpenMVS locally, run the corrected PROJ launcher on pinned Seneca, and validate the resulting raster if produced. Capture evidence, delete temporary workflow and record unresolved risks.
<!-- SECTION:PLAN:END -->
