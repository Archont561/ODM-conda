---
id: TASK-54
title: Resolve OpenMVS restricted third-party source and reduced target licensing
status: In Progress
assignee: []
created_date: '2026-10-28 15:48'
updated_date: '2026-10-28 15:48'
labels:
  - openmvs-odm
  - license
  - packaging
milestone: m-7
dependencies:
  - TASK-9
ordinal: 54000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Establish redistribution and corresponding-source obligations for pinned IBFS and TRWS files with owner or qualified review
- [ ] #2 Prove the supported ReconstructMesh build excludes restricted code and shipped headers or document an independently licensed alternative
- [ ] #3 Record the actual package and source-bundle contents and required notices before release
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Pinned OpenMVS libs/Math/IBFS/license.txt (SHA256 9e2ccaeb2fd1b11a6615b136b0d3e43078e1bf1de68f28e47efc9241bcfffb0f) says use is for research only; original local ReconstructMesh linked IBFS symbols. TRWS LICENSE.TXT (SHA256 fdffce5aade1171223b7aa2d6d8544971b3f2af101035aa9d40d36e8b24a5ed7) permits non-commercial use and distribution only. Original MVS target compiles SceneDensify.cpp, which uses TRWS; its archive also includes restricted headers. Whether and how the full original archives may be redistributed in corresponding-source bundles requires qualified review; changing build selection does not remove those files from source archives or resolve that issue.
<!-- SECTION:NOTES:END -->
