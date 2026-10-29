---
id: TASK-55
title: Resolve PoissonRecon bundled libpng security and linkage evidence
status: In Progress
assignee: []
created_date: '2026-10-28 22:40'
updated_date: '2026-10-29 07:24'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Trace pinned PoissonRecon build and linker inputs; add a fail-closed, tested linkage guard or mitigation; document limitations and run local checks. Obtain owner native validation before closing the task; preserve release gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-29: a reduced FAST_COMPILE -O0 research build linked bundled libmypng.a and contained the advisory-named png_handle_pCAL, png_read_png and png_set_text_2 symbols; this is not proof about the historical/full package or exploitability. Proposed build 2 patches the Poisson target to host libpng >=1.6.59,<1.7, checks a GNU link map and packages a path-free input inventory/hash, audits ELF NEEDED, and runs gray/RGB/RGBA adapter round trips. The patched reduced build, map guard and sphere fixture passed; local pixi check and focused tests passed. Local native build applied patch but failed solving compiler packages because conda-forge repodata returned EOF; no package, fresh retest or package audit exists. Source bundle assembled from hash-verified cache for research only. Owner must dispatch build.yml on proposed commit and review actual artifact, runtime, security and license evidence. No release gates changed; all acceptance criteria remain open. See research/poissonrecon-readiness-review.md.
<!-- SECTION:NOTES:END -->
