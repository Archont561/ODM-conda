---
id: TASK-2
title: Resolve pinned FPCFilter sampling without normals
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 23:55'
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
- [x] #1 A generated no-normals near-duplicate PLY fixture demonstrates the original behavior and verifies the chosen fix or documented limitation.
- [x] #2 Normals-bearing PLY sampling and pass-through remain covered and pass.
- [ ] #3 Any patch, modified-source notice, license expression, source archive and build number are reviewed; all affected release acknowledgements are reset.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reproduced on upstream 6e0c1c0 (g++ -O2): no-normals radius 0.5 on 6 points in 2 clusters kept 6, expected 2. Root cause: FastSampleFilter::run() erased from a local copy of file.points in the no-normals branch.

Fix: local patch recipes/fpcfilter/patches/0001-Write-no-normals-radius-sampling-results-back.patch, build number 1.

Verified:
- Functional regression (6 -> 2, one point per cluster) fails on the original binary and passes on the patched binary.
- Normals+radius, normals without radius and no-normals pass-through outputs are byte-identical to upstream.
- Random 3000-point property check: kept pairs are all >= radius apart.
- pixi run check; build, test, audit and sources --component fpcfilter pass. Artifact fpcfilter-0.2-h873e7db_1.conda; bundle source-fpcfilter-0.2-b1.tar.gz.
- Rattler warns about overdepending on _openmp_mutex (pre-existing recipe, unchanged).

ODM impact: OpenSfM export_ply writes no normals, so --fast-orthophoto with --pc-sample > 0 hit this bug. The default OpenMVS dense cloud carries normals (libs/MVS/Scene.cpp) and is not affected, by source reading only.

NOT done: AC #3. The patch, modified-source notice (SOURCE.txt now says Modified: yes), license expression and build number 1 need human review. Release checks remain false. Test tag bumped to fpcfilter-v0.2-b1 in tests/test_helpers.py.

Packaged A/B (build 0 rebuilt from commit 825ba09, artifact fpcfilter-0.2-h873e7db_0.conda, outside the repo; build 1 artifact in output/linux-64): the current no-normals regression test fails on build 0 (kept 6 of 6) and passes on build 1. Build 0 installs no patch notice in SOURCE.txt, as expected.

Decision (project owner): accept the local patch 0001 as the workaround; no upstream PR. Build 1 is the candidate pending explicit confirmation. License: upstream LICENSE is GPL-3.0 text with no or-later grant, so GPL-3.0-only AND BSD-2-Clause AND MIT is the accurate expression; AC #3 stays open until TASK-3 confirms it. Permissive relicensing needs the upstream copyright holders or a clean-room MIT/BSD reimplementation (see review packet doc-10, section 7).
<!-- SECTION:NOTES:END -->
