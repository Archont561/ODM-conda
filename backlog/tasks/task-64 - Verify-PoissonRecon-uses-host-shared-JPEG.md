---
id: TASK-64
title: Verify PoissonRecon uses host shared JPEG
status: Done
assignee: []
created_date: '2026-10-29 23:34'
updated_date: '2026-10-29 23:45'
labels:
  - poissonrecon-odm
dependencies: []
ordinal: 64000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Fail closed on bundled or static JPEG inputs and require host-prefix shared JPEG in the native link map.
- [x] #2 Require corresponding shared JPEG evidence in package audit with positive and negative tests.
- [x] #3 Run native build, fresh test and package audit privately, without changing release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Extend existing PNG link-map and packaged evidence guards to check JPEG; test genuine linker maps and adversarial input; validate privately in a native runner.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented strict host libjpeg.so map validation plus static/bundled JPEG rejection, and package evidence/DT_NEEDED checks; toy native map and negative tests pass. Native run 40974102649 passed build, installed/fresh tests and audit without upload or gate changes; qualified license/source review remains open in TASK-56.
<!-- SECTION:NOTES:END -->
