---
id: TASK-89
title: Build private Conda ODM fast-orthophoto application candidate
status: Done
assignee: []
created_date: '2026-10-30 20:34'
updated_date: '2026-10-30 21:07'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 89000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a pinned local-only ODM application recipe with relocatable launcher and explicit component dependencies.
- [x] #2 Build and install the candidate with actual compatible component packages and test its launcher and a real pipeline privately.
- [x] #3 Document exact scope and remaining publication blockers without weakening gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Package the existing prefix-adapted ODM prototype as a local-only Conda candidate; declare actual component and runtime dependencies, then test a fresh privately assembled environment and Seneca pipeline. Preserve release gates and record any unvalidated inputs.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41124481691 built odm-fast-research 3.6.2 hb0f4dca_0 SHA256 33edc1236acad9b6bb96764bfc9156d9536cc42717f1139316d31ec426fae044 and solved nine actual components through its Conda dependencies. Separately added five PyPI requirements; moved exact lock and channel, replayed in an isolated fresh prefix (425 matching Conda records; lock SHA256 3509f09317a47e7aeef40e27a29295b2fd776e0a112364d450669e29e17b2cb6), and passed installed launcher, Seneca pipeline and raster sanity. Rattler build skipped its own test phase; integration tested the installed package. Archive, lock and imagery discarded. Not self-contained or publishable; rights, dependency packaging, unique identities, audits and owner release gates remain open.
<!-- SECTION:NOTES:END -->
