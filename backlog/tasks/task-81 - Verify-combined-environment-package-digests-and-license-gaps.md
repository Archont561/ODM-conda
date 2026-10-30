---
id: TASK-81
title: Verify combined environment package digests and license gaps
status: Done
assignee: []
created_date: '2026-10-30 16:26'
updated_date: '2026-10-30 17:05'
labels:
  - research
  - integration
dependencies: []
ordinal: 81000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hash exact nine local binaries used by fresh combined environment
- [x] #2 Investigate OpenVINO license metadata with provenance and limitations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Hash every input file during the private integration run and trace exact OpenVINO metadata to upstream conda packaging evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hash-matched all 13 2025.4.1 build-1 OpenVINO binary archives from restored bundle to the recorded inventory. info/index and info/about license fields and info/licenses are absent; about lists four license_file paths and exact feedstock c362bec1c4eaf45e8f4b9e9f61847b97aba06045. Recipe top-level Apache-2.0 is not a full license/notice conclusion. Details in research/openvino-binary-license-metadata.json and inventory notes.

Private run 41090003564 independently hashed all nine exact local binaries used in the fresh solve; read-only recovery 41095611381, full identities recorded in combined inventory notes. Optional local archive hash inventory helper added with unit tests; it was not used in that native run.
<!-- SECTION:NOTES:END -->
