---
id: TASK-92
title: Make private ODM build and lock replay repeatable
status: In Progress
assignee: []
created_date: '2026-10-30 23:13'
updated_date: '2026-10-30 23:13'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 92000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Build all compatible ODM component and source runtime candidates from pinned sources without relying on expiring build artifacts.
- [ ] #2 Assemble and retain an access-controlled private channel and exact lock, then validate replay and ODM integration in a fresh prefix.
- [x] #3 Document commands, verification evidence, and unresolved distribution and reproducibility limits without weakening release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Build all local component packages and five source-based runtime candidates from pinned inputs, index them privately, generate and retain the Pixi manifest/lock/channel only in a new owner-controlled external directory, verify exact hashes and relocated replay, and run an optional pinned dataset integration without uploading outputs.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hosted run 41145494232 built all 15 packages from pinned inputs, assembled a private channel and Conda-only lock, and replayed a relocated copy in a fresh prefix with 456 matching installed Conda identities and hashes. The installed ODM launcher, pinned Seneca dataset and raster sanity passed. All hosted bundles and outputs were discarded, so owner-controlled durable retention remains outstanding; no package was published. ODM rattler package tests were skipped, with installed application integration tested instead. See research/odm-fast-orthophoto-prototype.md for commands, limitations and evidence.
<!-- SECTION:NOTES:END -->
