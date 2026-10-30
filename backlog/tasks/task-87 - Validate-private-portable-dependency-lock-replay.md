---
id: TASK-87
title: Validate private portable dependency lock replay
status: Done
assignee: []
created_date: '2026-10-30 19:26'
updated_date: '2026-10-30 19:54'
labels:
  - research
  - integration
dependencies: []
ordinal: 87000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create private lock and verified local package set without publishing binaries
- [x] #2 Replay exact lock in relocated fresh prefix and validate integration
- [x] #3 Document source, notice and portability limitations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Build private variants, create isolated original lock and archive set, relocate byte-identical lock/manifest and packages, replay with a fresh prefix and compare inventories, then run private Seneca and raster checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41115458840 generated a lock from a loopback-only private channel, moved unchanged lock/manifest and all nine verified archives, removed original channel, and passed pixi install --locked with isolated replay cache and fresh prefix. Lock SHA256 fb28601ad4ef3ee2c4327a825ba098e49b0ed1f34b109ecd9a2405d009516681; 424 Conda identity/hash/URL records matched, then preflight, scoped guards, Seneca and raster sanity passed. Snapshot recovered by 41118954520; lock, binaries and imagery discarded. Not offline/cross-platform, not a wheel byte audit, and rights/source/license gates remain open.
<!-- SECTION:NOTES:END -->
