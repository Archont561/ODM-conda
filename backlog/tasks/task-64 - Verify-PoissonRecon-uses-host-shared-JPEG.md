---
id: TASK-64
title: Verify PoissonRecon uses host shared JPEG
status: In Progress
assignee: []
created_date: '2026-10-29 23:34'
updated_date: '2026-10-29 23:34'
labels:
  - poissonrecon-odm
dependencies: []
ordinal: 64000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fail closed on bundled or static JPEG inputs and require host-prefix shared JPEG in the native link map.
- [ ] #2 Require corresponding shared JPEG evidence in package audit with positive and negative tests.
- [ ] #3 Run native build, fresh test and package audit privately, without changing release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Extend existing PNG link-map and packaged evidence guards to check JPEG; test genuine linker maps and adversarial input; validate privately in a native runner.
<!-- SECTION:PLAN:END -->
