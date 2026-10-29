---
id: TASK-60
title: Run corrected disposable ODM Seneca dataset trial
status: Done
assignee: []
created_date: '2026-10-29 21:41'
updated_date: '2026-10-29 22:10'
labels:
  - integration
dependencies: []
ordinal: 60000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Assemble published components and local-only research components in a disposable Linux prefix and run corrected ODM fast-orthophoto on the pinned Seneca dataset.
- [x] #2 If the workflow completes, independently inspect final GeoTIFF dimensions, coordinate system, geotransform, bands and statistics; otherwise record exact blocker without claiming success.
- [x] #3 Record package identities, run evidence and limits; do not upload research components or dataset outputs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a temporary restricted GitHub Actions workflow to obtain and verify published and research-only inputs, rebuild and retest OpenSfM and OpenMVS locally, run the corrected PROJ launcher on pinned Seneca, and validate the resulting raster if produced. Capture evidence, delete temporary workflow and record unresolved risks.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Run 40960012356 completed the corrected fast-orthophoto Seneca trial in a disposable Ubuntu 24.04 prefix using the four hash-verified published packages and five local-only components. It rebuilt, fresh-retested and audited OpenSfM/OpenMVS; launcher preflight passed with prefix PROJ paths. The command completed and gdalinfo inspected the final 9574 x 10488 RGBA GeoTIFF in EPSG:32617 and its band statistics; a nonempty PDF report existed. No research sources, binaries, images or outputs were uploaded. Metadata and statistics do not establish visual quality, crop completeness, geographic accuracy, dataset rights, relocation or redistribution readiness; TASK-13 stays open.
<!-- SECTION:FINAL_SUMMARY:END -->
