---
id: TASK-84
title: Investigate newer OpenVINO for combined ODM environment
status: Done
assignee: []
created_date: '2026-10-30 17:17'
updated_date: '2026-10-30 17:33'
labels:
  - research
  - integration
dependencies: []
ordinal: 84000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Test a newer OpenVINO solve with the nine component binaries and document compatibility
- [x] #2 Inspect exact selected binaries source and license notices or document blockers
- [x] #3 Run affected combined integration tests if a compatible solve is available
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Privately rebuild and validate the nine-component environment with a newer OpenVINO candidate, inspect exact package metadata/notices, and run Seneca when compatible; record scoped findings without release approval.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private combined run 41097529820 built candidates but failed solve: OpenMVS requires OpenCV 4.12.0, available builds require OpenVINO 2025, incompatible with >=2026. Seneca/preflight blocked and not run. Standalone OpenCV 4.13/OpenVINO 2026.4.1 solved but not nine-component tested. Inspected hash-identified 2026.0 b1 (13 metadata licenses, no info/licenses), 2026.4.1 b1 (13 with notice paths), and alternative-solve b0 (14 with notice paths). Main 2026.4.1 source archive hash and four notice hashes match; third-party inputs and legal sufficiency remain open. No production dependencies changed.
<!-- SECTION:NOTES:END -->
