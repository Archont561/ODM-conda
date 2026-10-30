---
id: TASK-73
title: Build scoped OpenSfM from reduced source candidate
status: Done
assignee: []
created_date: '2026-10-30 14:03'
updated_date: '2026-10-30 14:13'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 73000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Validate reduced source graph and build scoped package without omitted assets
- [x] #2 Run native build, installed and fresh tests and scoped audit
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verify the pinned reduced staged source graph and build a private scoped recipe; retain original behavior and audit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41068961668 built scoped OpenSfM from reduced source candidate SHA256 3f36288338532cee3bf5797b3031868b06b0a29eeb1adbd44905f1f3bf2f2fef; exact 874-file patched graph fingerprint 74c5be8ef66a189a8001816e7564e6b83144856dff176ca2674798f7b809b6d9. Installed/fresh tests and scoped audit passed; package SHA256 0c1bf13c2ab66aa5c21b8e41e924d98a9402f0acb674793921264a22caa0e3e6, discarded. No dataset integration on this package, original archive fetched privately and dependency/source/rights remain unresolved under TASK-36.
<!-- SECTION:NOTES:END -->
