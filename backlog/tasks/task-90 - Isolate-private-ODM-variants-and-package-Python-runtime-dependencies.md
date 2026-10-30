---
id: TASK-90
title: Isolate private ODM variants and package Python runtime dependencies
status: Done
assignee: []
created_date: '2026-10-30 21:12'
updated_date: '2026-10-30 22:30'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 90000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Give private ABI/source variants Conda identities distinct from production artifacts.
- [x] #2 Package the previously separate Python dependencies or document precisely blocked inputs without concealing them.
- [x] #3 Validate a fresh ODM environment without separately adding PyPI dependencies where feasible, and record remaining release blockers.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use explicit research build strings for ABI/source variants and inspect exact pinned Python wheels and source packaging. Test private channel solve and integration without weakening release gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41129908688 built research-tagged OpenCV 4.13 orthophoto, reduced Poisson, scoped OpenSfM and reduced OpenMVS plus five separately named Conda repacks of SHA-pinned upstream wheels. Installed ODM via a loopback channel with no PyPI lock entries, replayed a byte-identical lock in a relocated fresh prefix (440 matching Conda records, SHA256 8fadfcfd5fdcf973491b46bcc92022eeeaa457a5eb2c156a6cb9d267e812aac0), and passed the installed launcher, Seneca pipeline and raster sanity. Wheel imports/fresh tests passed in 41129610665; JPEG XL round-trip separately passed 41132661773. Research-only wheel repacks are not source builds; JPEG XL contains native code. Source completeness, rights, native audit and owner release gates remain open; no binaries/lock/dataset retained.

Repeat integration 41134867203 included the JPEG XL round-trip test and bumped odm-fast-research build 1 to avoid reusing build 0 identity after dependency metadata changes. Package SHA256 e89cf0198902e01c9b3e5970bdbf93d6081c9fea4fff2dc2c896b7fe20e23a60; relocated Conda-only replay lock 551ba9fa9d15ebdfd47dab13a629b1e8d39c60362e0ff38875af3922faa5cffe matched 440 records and passed launcher, Seneca and raster sanity. Research binaries, lock and outputs discarded; source/license/release gates remain open.
<!-- SECTION:NOTES:END -->
