---
id: TASK-55
title: Resolve PoissonRecon bundled libpng security and linkage evidence
status: To Do
assignee: []
created_date: '2026-10-28 22:40'
labels: []
dependencies: []
references:
  - 'https://github.com/advisories/GHSA-mmpj-hr4h-5g99'
  - 'https://github.com/advisories/GHSA-m968-rq7m-646j'
priority: high
type: bug
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pinned upstream source builds libpng 1.2.29 into a static archive; historical native output has not been inspected for its final linkage or reachable PNG paths. Historical advisories cover the source version, but exploitability in this binary is unproven. Resolve before release; see research/poissonrecon-readiness-review.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Determine exact final link inputs and runtime dependencies from a current native build, with retained linker map or equivalent evidence and tests.
- [ ] #2 Eliminate or responsibly mitigate any vulnerable bundled implementation present in the executable and test the relevant input/output paths; document any non-reachability argument.
- [ ] #3 Repeat native build, fresh retest, package audit and source-bundle review; preserve release gates pending owner and security/license review.
<!-- AC:END -->
