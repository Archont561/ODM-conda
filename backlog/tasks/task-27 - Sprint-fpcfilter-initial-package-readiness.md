---
id: TASK-27
title: 'Sprint: fpcfilter initial package readiness'
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 16:00'
labels:
  - sprint
  - coordination
  - fpcfilter
milestone: m-1
dependencies:
  - TASK-2
  - TASK-25
  - TASK-26
  - TASK-3
type: task
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
One undated delivery coordinator for the fpcfilter package milestone. Execute concrete prerequisite work, not this coordinator as a substitute for implementation: TASK-2, TASK-25, TASK-26, TASK-3. Upstream package gates are dependencies of the applicable implementation task. Shared legal/publisher/platform work stays cross-cutting. No calendar, assignee, native version bump or publication is implied.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every explicit prerequisite task is Done with its acceptance evidence; do not close this Sprint while a dependency remains open or blocked.
- [x] #2 The package's implementation/validation and independent readiness review are linked, with exact source/artifact identities, known limitations and any remaining owner actions stated honestly.
- [x] #3 Close only this planning/readiness gate after the work is verified; no automatic release flags, public upload, deadline or support claim follows from Sprint completion.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Closed 2026-10-27: the last open prerequisite was TASK-3, completed with the
owner's dem2points approval in the same changeset (all fpcfilter-side items of
TASK-3 were resolved earlier).

AC #1: every prerequisite is Done with acceptance evidence — TASK-2 (owner
approval of patch 0001/license/build 1, doc-10), TASK-25 (validation from CI:
definitive run
[40515263476](https://github.com/Archont561/ODM-conda/actions/runs/40515263476)
plus the green build stages of the three earlier attempts), TASK-26
(independent readiness review recorded), TASK-3 (Done 2026-10-27). The
publisher itself was proven by the real publication (TASK-15).

AC #2: validation (TASK-25) and review (TASK-26) are linked with exact
identities — tag `fpcfilter-v0.2-b1` == published `main` HEAD `9f6ee33`,
artifact `fpcfilter-0.2-h873e7db_1.conda` (channel repodata sha256
`8d3949bf…`, attestation `d168ed89…`), durable source asset
`source-fpcfilter-0.2-b1.tar.gz` (551,633 B) on the live Release. Known
limitations (doc-10 §8): linux-64 CPU only, no ODM end-to-end, pre-existing
`_openmp_mutex` over-dependency warning. Remaining owner actions: none for
this milestone — publication already happened (2026-10-27).

AC #3: this closure is the planning/readiness gate only; the fpcfilter
release flags were enabled by the earlier explicit owner approval
(TASK-2/doc-10) and publication was a separate deliberate Release. No
automatic upload, deadline or support claim follows from this Sprint.
<!-- SECTION:NOTES:END -->
