---
id: TASK-59
title: Validate published components together in a fresh Linux environment
status: Done
assignee: []
created_date: '2026-10-29 21:23'
updated_date: '2026-10-29 21:27'
labels:
  - integration
dependencies: []
ordinal: 59000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Install all four exact published builds together from the channel and capture the resolved dependency identities.
- [x] #2 Run each installed component generated fixture and linkage check in that same environment.
- [x] #3 Record scope, limitations and next dataset prerequisites without uploading data or research packages.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Run a disposable least-privilege GitHub Actions integration job for the four published builds, run installed fixtures in one prefix, capture the solve and report failures; remove temporary workflow and record evidence before final PR.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Run 40957790376 installed exact four published builds and Python/GDAL/OpenCV/PDAL/ExifTool in one Ubuntu 24.04 prefix; verified the four published SHA256 identities, all four installed generated fixtures and ldd checks, plus Python imports. All 322 solver filename/hash records are captured in the research inventory. Fixtures are separate synthetic tests, not a chained or end-to-end ODM dataset test; local-only research package build and corrected dataset trial remain prerequisites under TASK-13.
<!-- SECTION:FINAL_SUMMARY:END -->
