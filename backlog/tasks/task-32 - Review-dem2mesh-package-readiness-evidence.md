---
id: TASK-32
title: Review dem2mesh package-readiness evidence
status: To Do
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-28 20:12'
labels:
  - packaging
  - review
  - dem2mesh
milestone: m-4
dependencies:
  - TASK-6
type: task
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-6 for the dem2mesh milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review deterministic mesh output, the installed GDAL linkage and the complete pinned meshing source graph. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim evidence triage: research/component-readiness-review.md records run IDs, artifact identities, source evidence and limitations. Per-recipe files match the historical native run but shared scripts changed; actual retained artifact/source inspection, current-commit native evidence as appropriate, dependency notices and qualified release review remain open. This is not approval and prerequisites and acceptance criteria remain unchecked.

2026-10-29: local batch review verified pinned archive bytes, extracted declared notice inputs and checked deterministic temporary source bundles and every manifest entry. Current-commit local native build was blocked by conda-forge repodata EOF; owner-dispatched batch validation and artifact review remain necessary. See research/component-readiness-review.md for component-specific evidence and limitations. Release gates remain false.
<!-- SECTION:NOTES:END -->
