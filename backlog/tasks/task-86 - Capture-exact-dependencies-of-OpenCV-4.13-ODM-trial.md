---
id: TASK-86
title: Capture exact dependencies of OpenCV 4.13 ODM trial
status: Done
assignee: []
created_date: '2026-10-30 18:42'
updated_date: '2026-10-30 19:09'
labels:
  - research
  - integration
dependencies: []
ordinal: 86000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Run fresh nine-component private trial with validated locked resolution
- [x] #2 Record sanitized exact Conda and PyPI identities including local package hashes and OpenVINO versions
- [x] #3 Document replay limitations and unresolved license/source gaps
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Rebuild private 4.13 variants, install nine components in a fresh locked combined environment, capture sanitized lock-derived records and hashes, exercise the pipeline, and record replay and rights limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41109317029 built/retested/audited variants, validated pixi install --locked in place, solved nine packages and passed Seneca/raster checks. Read-only run 41112705697 recovered 424 installed Conda records, 16 PyPI lock records, nine independently hashed local binaries and lock SHA256 into sanitized research JSON. Exact resolved libopenvino 2026.2.1 h1f0fae8_1. Original lock/local files not retained, separate clean-prefix exact-lock replay not performed, and license/source/dataset rights remain open. This is a new solve, not proof of previous trial versions.
<!-- SECTION:NOTES:END -->
