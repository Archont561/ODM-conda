---
id: TASK-2
title: Resolve pinned FPCFilter sampling without normals
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - bug
  - upstream
  - fpcfilter
milestone: m-1
dependencies: []
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Observed while validating upstream commit 6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b (ODM tag 331): ASCII PLY pass-through works, but radius sampling without normals retains all six generated points. In fastsamplefilter.hpp the non-normals branch erases from a local copy without assigning it back to file.points. The starter test covers pass-through and the working normals-bearing binary branch; it does not claim this bug is fixed. Choose a reviewed patch, a compatible new pin, or a clearly documented supported-use limitation before approval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A generated no-normals near-duplicate PLY fixture demonstrates the original behavior and verifies the chosen fix or documented limitation.
- [ ] #2 Normals-bearing PLY sampling and pass-through remain covered and pass.
- [ ] #3 Any patch, modified-source notice, license expression, source archive and build number are reviewed; all affected release acknowledgements are reset.
<!-- AC:END -->
