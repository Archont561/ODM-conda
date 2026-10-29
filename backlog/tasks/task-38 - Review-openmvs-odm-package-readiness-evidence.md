---
id: TASK-38
title: Review openmvs-odm package-readiness evidence
status: To Do
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-28 20:12'
labels:
  - packaging
  - review
  - openmvs-odm
milestone: m-7
dependencies:
  - TASK-9
  - TASK-53
  - TASK-54
type: task
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-9 for the openmvs-odm milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review a CPU-only installed-prefix reconstruction fixture, VCG/Eigen source coverage, exact ODM patches and AGPL obligations; CUDA is not implied. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim research-only evidence and unresolved source/license blockers are recorded in research/open-components-license-review.md; the relevant owner-dispatched native build/fresh retest/limited audit passed, but temporary outputs were removed. No production artifact, comprehensive dependency or source audit, license approval or release decision follows. Prerequisites and acceptance criteria remain unchecked.

2026-10-29: OpenMVS archives and four-patch research tree fingerprint locally re-verified. Fixed unregistered production builder omission of the installed mesh-cleaning helper; this is not production recipe integration. New research identity/dependency audit requires owner dispatch; restricted-source, notices and ABI gates remain open.
<!-- SECTION:NOTES:END -->
