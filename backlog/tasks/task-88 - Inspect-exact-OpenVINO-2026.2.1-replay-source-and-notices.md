---
id: TASK-88
title: Inspect exact OpenVINO 2026.2.1 replay source and notices
status: Done
assignee: []
created_date: '2026-10-30 20:09'
updated_date: '2026-10-30 20:18'
labels:
  - openvino
  - license
  - research
dependencies: []
ordinal: 88000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Verify the exact replay-selected OpenVINO archives and record their source and license metadata.
- [x] #2 Compare pinned primary source and notices where practical, recording unverified inputs and legal limits.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Privately inspect SHA-verified exact replay archives and rendered recipes; compare named source pins and notice hashes to upstream where feasible. Record bounded evidence and unresolved rights; do not publish archives.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Run 41121075671 inspected all 13 exact SHA-verified replay-selected archives: metadata Apache-2.0, feedstock SHA 60076581dd7818d779760e0937f869dfe992eb7b, four info/licenses hashes equal verified primary source. Independently fetched seven rendered linux-64 source archives and checked all declared SHA256 pins. Metadata retained, archives discarded; patches, transitive sources, source completeness and legal applicability remain unverified.
<!-- SECTION:NOTES:END -->
