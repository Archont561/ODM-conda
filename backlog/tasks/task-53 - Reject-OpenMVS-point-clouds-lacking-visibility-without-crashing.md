---
id: TASK-53
title: Reject OpenMVS point clouds lacking visibility without crashing
status: In Progress
assignee: []
created_date: '2026-10-28 15:11'
updated_date: '2026-10-29 08:05'
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

Trace the exact OpenMVS PLY camera-visibility format, build a generated valid separate-PLY fixture and test both valid and missing visibility through the existing research installed-prefix workflow; record native and production/legal limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28: unpatched ReconstructMesh built with GCC 12 segfaulted (-11) on 400 generated PLY points both with no views property and with scalar views counts. Research patch openmvs-visibility-check.patch SHA256 74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90 prevents interpretation of a scalar count as view indices and rejects absent/invalid camera visibility before reconstruction. Patched local mixed-environment executable produced a diagnostic and exit 1 on both inputs; existing cube-clean and sparse point-cloud scene fixtures still passed. This is not a package validation, proof of support for external PLY with camera indices, a complete malformed-input safety audit, or owner approval.

The synthetic MVSI fixture also exercises the patched research executable against separate PLY without camera IDs and scalar-count-only PLY; both fail cleanly. Valid separate PLY support remains unproven and the patch is not integrated into a package.

2026-10-28: local-only native research run 40759635611 at a656bdb passed installed and fresh-environment functional fixtures including generated valid scene and missing-visibility rejection. This does not establish separate PLY input with valid camera indices, production-package coverage, source bundle and notices, or release approval; acceptance criteria remain open.


Research build 2: added strict explicit uint32 camera-index list loading and regression fixtures. The four-patch SHA-verified staged tree compiled locally; generated-scene and separate ASCII PLY reconstruction (53 vertices / 46 faces), rejection of missing, invalid and unordered IDs and invalid schemas, and generated cube cleaning passed. Fourth patch SHA256 `c3b350097791445ff222de26d4791e13d2737af9133271a22aac945cce0d5560`; staged tree fingerprint `847c18300e7a6909a4ca4bc18fa6ea43efb1801097369a768e75536de19fdcfd`. This local build-tree evidence alone was not installed-prefix validation; binary PLY and general malformed-file safety remain unverified. Production integration, source bundle, notices/legal, ABI and owner approval remain open; do not mark Done.

2026-10-29: owner confirmed selecting OpenMVS for local-only research run [40840595990](https://github.com/Archont561/ODM-conda/actions/runs/40840595990), at commit d63550f. The workflow passed the build, installed-prefix recipe tests, fresh package retest, and limited research audit. This supports the research package only; it does not resolve production integration, corresponding source, comprehensive notices/legal review, ABI, or approval. No packages or sources were uploaded.

2026-10-29: expanded local tests revealed the upstream PLY parser does not swap non-native binary scalars: a generated big-endian PLY with ID 0 was silently accepted with misinterpreted coordinates. Research build 3 rejects non-native byte order before reading the point-cloud body. Recompiled locally, ASCII with and without scalar views, little-endian binary and big-endian clean rejection passed with all previous fixture cases. Fourth patch now SHA256 `4dbaa9e4fa186ce80f6c3f220c67a89bf80fea347bf798bd64a80fc096f03d6d`, staged fingerprint `25a71e02cecf70460d78543c104d8d14e9c5b65456183e96c1674d696f60d217`. Owner-dispatched native package test for build 3 is still required; run 40840595990 applies to build 2 only. Production, rights, notices, ABI and general malformed-input handling remain open.
<!-- SECTION:NOTES:END -->
