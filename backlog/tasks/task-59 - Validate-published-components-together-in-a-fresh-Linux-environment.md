---
id: TASK-59
title: Validate published components together in a fresh Linux environment
status: In Progress
assignee: []
created_date: '2026-10-29 21:23'
updated_date: '2026-10-29 21:23'
labels:
  - integration
dependencies: []
ordinal: 59000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Install all four exact published builds together from the channel and capture the resolved dependency identities.
- [ ] #2 Run each installed component generated fixture and linkage check in that same environment.
- [ ] #3 Record scope, limitations and next dataset prerequisites without uploading data or research packages.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Run a disposable least-privilege GitHub Actions integration job for the four published builds, run installed fixtures in one prefix, capture the solve and report failures; remove temporary workflow and record evidence before final PR.
<!-- SECTION:PLAN:END -->
