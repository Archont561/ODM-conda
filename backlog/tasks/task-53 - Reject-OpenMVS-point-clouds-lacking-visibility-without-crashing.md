---
id: TASK-53
title: Reject OpenMVS point clouds lacking visibility without crashing
status: In Progress
assignee: []
created_date: '2026-10-28 15:11'
updated_date: '2026-10-28 20:11'
labels:
  - openmvs-odm
  - packaging
milestone: m-7
dependencies:
  - TASK-9
priority: high
type: bug
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pinned ODM OpenMVS ReconstructMesh crashes on a separate PLY point cloud with no per-point camera IDs, including one with a scalar views count. Provide safe validation without inventing visibility and verify the production package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Plain and scalar-views PLY inputs without camera IDs fail with an explicit diagnostic and no crash.
- [ ] #2 Valid scene reconstruction and mesh cleaning continue to pass, including through installed-prefix native CI.
- [ ] #3 Reviewed patch, source bundle, notices, ABI and remaining limitations are recorded before marking Done.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Keep a research patch and regression fixture; review and integrate the patch into the pinned production source graph when the OpenMVS recipe is ready; validate good and bad inputs in a fresh installed package.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28: unpatched ReconstructMesh built with GCC 12 segfaulted (-11) on 400 generated PLY points both with no views property and with scalar views counts. Research patch openmvs-visibility-check.patch SHA256 74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90 prevents interpretation of a scalar count as view indices and rejects absent/invalid camera visibility before reconstruction. Patched local mixed-environment executable produced a diagnostic and exit 1 on both inputs; existing cube-clean and sparse point-cloud scene fixtures still passed. This is not a package validation, proof of support for external PLY with camera indices, a complete malformed-input safety audit, or owner approval.

The synthetic MVSI fixture also exercises the patched research executable against separate PLY without camera IDs and scalar-count-only PLY; both fail cleanly. Valid separate PLY support remains unproven and the patch is not integrated into a package.

2026-10-28: local-only native research run 40759635611 at a656bdb passed installed and fresh-environment functional fixtures including generated valid scene and missing-visibility rejection. This does not establish separate PLY input with valid camera indices, production-package coverage, source bundle and notices, or release approval; acceptance criteria remain open.
<!-- SECTION:NOTES:END -->
