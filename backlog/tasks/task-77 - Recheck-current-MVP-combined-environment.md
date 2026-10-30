---
id: TASK-77
title: Recheck current MVP combined environment
status: Done
assignee: []
created_date: '2026-10-30 14:21'
updated_date: '2026-10-30 15:12'
labels:
  - research
  - integration
dependencies: []
ordinal: 77000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Install current private research and published MVP components in fresh environment
- [x] #2 Test selected imports, executables and dependencies and record identities
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Install current actual packages and preflight selected imports and executables in a fresh environment.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Prepared a private nine-package preflight including current reduced-source OpenSfM, Poisson and OpenMVS, but GitHub/API TLS handshakes failed before workflow push/dispatch. Current package combination was not installed or tested. Prior run 41066302285 covers a different combination.

Private run 41072814562 built current reduced-source Poisson, OpenSfM and reduced-copy OpenMVS build 4; installed them with six pinned artifacts in a fresh Pixi environment; selected imports, binaries, guard and preflight passed. Nine package SHA256s and selected GDAL/PDAL/OpenCV identities recorded in research/odm-fast-orthophoto-prototype.md. No full transitive dependency or general ABI assurance; no artifacts uploaded.
<!-- SECTION:NOTES:END -->
