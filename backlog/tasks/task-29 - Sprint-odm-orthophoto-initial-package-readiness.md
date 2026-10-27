---
id: TASK-29
title: 'Sprint: odm-orthophoto initial package readiness'
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 21:50'
labels:
  - sprint
  - coordination
  - odm-orthophoto
milestone: m-2
dependencies:
  - TASK-4
  - TASK-28
type: task
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
One undated delivery coordinator for the odm-orthophoto package milestone. Execute concrete prerequisite work, not this coordinator as a substitute for implementation: TASK-4, TASK-28. Upstream package gates are dependencies of the applicable implementation task. Shared legal/publisher/platform work stays cross-cutting. No calendar, assignee, native version bump or publication is implied.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every explicit prerequisite task is Done with its acceptance evidence; do not close this Sprint while a dependency remains open or blocked.
- [x] #2 The package's implementation/validation and independent readiness review are linked, with exact source/artifact identities, known limitations and any remaining owner actions stated honestly.
- [x] #3 Close only this planning/readiness gate after the work is verified; no automatic release flags, public upload, deadline or support claim follows from Sprint completion.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

AC #1: both explicit prerequisites are Done with acceptance evidence — TASK-4 (recipe, notices, fixture and machinery generalized; native validation run 40584231748 fully green after the PR #12 band-order and PR #14 pyc-leak fixes; owner approval recorded in its notes) and TASK-28 (independent readiness review with artifact/source identities, limitation statement and an explicit technically-ready decision).

AC #2 linkage: implementation/validation lineage `d6cf841` (PR #11, recipe+fixture) → `a9b96af` (PR #12, RGB band-order fix) → `d0aeb13` (PR #14, skip_pyc_compilation fix; PR #13's interim attempt was superseded and its premise corrected in the TASK-4 notes). Artifact identity `odm-orthophoto-0.0.0.dev20250225-h873e7db_0.conda` (114.05 KiB), source `55b66d87` (archive sha256 `a3f3410b…f5b528d2`), bundle sha256 `c02b61f6…bc0c68`, evidence set in run 40584231748 / CI artifact 12770762758. Known limitations restated: glibc 2.39 test host vs the `>=2.28` toolchain declaration, linux-64 only, no ODM end-to-end integration, fixture-level (not photogrammetric) correctness. Remaining owner actions at closure: merge the approval PR, tag `odm-orthophoto-v0.0.0.dev20250225-b0` on the approved HEAD, create the manual Release.

AC #3: this coordinator closes as a planning/readiness gate only. The release flags flipped in the same approval commit do so by explicit owner authorization, not automatically from sprint completion; no public upload, deadline or support claim follows.
<!-- SECTION:NOTES:END -->
