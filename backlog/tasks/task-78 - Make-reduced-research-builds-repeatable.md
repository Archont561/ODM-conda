---
id: TASK-78
title: Make reduced research builds repeatable
status: Done
assignee: []
created_date: '2026-10-30 15:38'
updated_date: '2026-10-30 15:51'
labels:
  - research
dependencies: []
ordinal: 78000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Provide local-only runner for three reduced candidates without transient source edits
- [x] #2 Native-build, fresh-test and audit variants or document concrete blockers
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Add explicit reduced OpenMVS builder and disposable runner for three candidates with unchanged audits; native validate.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented disposable per-component reduced runner and explicit OpenMVS reduced recipe/wrapper; existing standard and production audits remain unchanged. Unit tests pass; three native matrix builds underway in run 41082954948.

Native private matrix run 41082954948 passed all three separate reduced-source runner selections, installed/fresh tests and corresponding research audits. Discarded package SHA256s Poisson 0ab40fee7fbabc56235b61e0eaf8aa3334f4d89f386f8eafbb9ee07356544b53, OpenSfM 6deb98c0b61108d8888d493917ab7a9e44dc1fadc8ae3230efa66e01c9896a42, OpenMVS 066edc5f5ce1533ed104c48b012164a81673920af9acd75622b19295adc753c3. Sequential all option unit-tested, not native-run; original source and legal gates remain open.
<!-- SECTION:NOTES:END -->
