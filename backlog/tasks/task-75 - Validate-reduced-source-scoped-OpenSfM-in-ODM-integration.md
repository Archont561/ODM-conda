---
id: TASK-75
title: Validate reduced-source scoped OpenSfM in ODM integration
status: In Progress
assignee: []
created_date: '2026-10-30 14:21'
updated_date: '2026-10-30 14:23'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 75000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build and audit reduced-source scoped OpenSfM privately
- [ ] #2 Install current MVP packages and run Seneca pipeline with scoped package
- [ ] #3 Record outputs and limitations without retaining artifacts
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a private workflow to build and audit reduced-source scoped OpenSfM and run the Seneca pipeline with current research packages.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Prepared a private Seneca integration workflow using the actual reduced-source scoped OpenSfM and Poisson research variants, but GitHub TLS handshakes failed before push/dispatch; no new native build or dataset trial ran. Prior run 40980893166 used earlier scoped package, not this reduced-source build.
<!-- SECTION:NOTES:END -->
