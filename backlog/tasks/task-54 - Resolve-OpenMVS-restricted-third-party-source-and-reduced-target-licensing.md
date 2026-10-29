---
id: TASK-54
title: Resolve OpenMVS restricted third-party source and reduced target licensing
status: In Progress
assignee: []
created_date: '2026-10-28 15:48'
updated_date: '2026-10-29 22:32'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement a deterministic local-only reduction for the exact patched source graph with a manifest and fail-closed checks; test negative cases and fresh native ReconstructMesh build from the reduced copy; record unresolved notice and rights review without distributing any source or binaries.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Pinned OpenMVS libs/Math/IBFS/license.txt (SHA256 9e2ccaeb2fd1b11a6615b136b0d3e43078e1bf1de68f28e47efc9241bcfffb0f) says use is for research only; original local ReconstructMesh linked IBFS symbols. TRWS LICENSE.TXT (SHA256 fdffce5aade1171223b7aa2d6d8544971b3f2af101035aa9d40d36e8b24a5ed7) permits non-commercial use and distribution only. Original MVS target compiles SceneDensify.cpp, which uses TRWS; its archive also includes restricted headers. Whether and how the full original archives may be redistributed in corresponding-source bundles requires qualified review; changing build selection does not remove those files from source archives or resolve that issue.

2026-10-28 license evidence: research/openmvs-notices.json hash-records 486 pinned files from the GCC 12 reduced-target Ninja dependency trace plus 13 separate root/third-party notices, including IBFS and TRWS license files; verification against the patched staged tree passed. SceneReconstruct.cpp explicitly grants AGPL v3 or later and additional attribution terms; compiled VCG complex.h grants GPL v2 or later; Eigen/Core states MPL 2.0, its COPYING.README identifies possible LGPL/BSD components, lmfit COPYING grants FreeBSD terms, and compiled tiny_gltf.h and json.hpp contain distinct notices. Trace inclusion is not proof of linked code, a complete inventory or compatibility. IBFS license says research use only and TRWS restricts distribution to non-commercial purposes; both remain present in the complete source archive even though the reduced binary has no matching IBFS/MRFEnergy symbols. Qualified review must resolve archive redistribution and corresponding-source scope, applicable license choices, dynamic dependency obligations and complete notices. Do not approve a final SPDX expression or release based on this triage.

2026-10-28: research/open-components-license-review.md records preliminary review of the restricted original archive, reduced target, VCG/Eigen/CGAL and incomplete notices. Native local-only run 40759635611 passed limited payload/RPATH audit but did not produce a retained linker map or authorize source redistribution. Corresponding-source scope, rights and qualified approval remain open; no package or archive may be published on this basis.

2026-10-28: local-only research builder now requests and fail-closed checks the actual ReconstructMesh GNU link map for named IBFS/TRWS/MRFEnergy and excluded dense/refine/texture inputs, while requiring expected reconstruction and library markers; the SHA256 is printed and the temporary map is not uploaded. Synthetic negative and real GNU toy-link tests pass. This guard requires an owner native research rerun and cannot prove code or source archive redistribution rights; all acceptance criteria remain open.

2026-10-28: owner-dispatched local-only run https://github.com/Archont561/ODM-conda/actions/runs/40762858939 at 4dba9fe141c22c4791f44a2ce330ef00bb6b5811 passed the actual reduced OpenMVS build and link-map guard, installed/fresh tests and limited leak/RPATH audit; temporary outputs were removed. Named-input matching is not a complete code or redistribution proof. No legal approval, production package, archive release or acceptance-criterion closure is implied.

2026-10-28: OpenMVS local-only research build 1 now carries and audits exact pinned COPYRIGHT.md, VCG LICENSE and Eigen COPYING.MPL2/COPYING.README notice texts. This is a limited subset, not complete license clearance or permission to distribute restricted archives. Full actual dependency inventory, notices and corresponding source remain open; an owner-dispatched build/retest/audit of changed research payload is required.

Reverified pinned source and examined reduced-build patch: Boost Graph fallback replaces enabled IBFS, excludes densify/texture/refine and removes IBFS/TRWS build globs, but original archive still contains restricted files. Rights-holder permission or separately reviewed reduced source tree are possible routes, neither implemented nor approved. Later upstream removes TRWS but changes IBFS and is not the pinned fork. See research/open-components-license-review.md.

2026-10-29: Disposable run 40965276525 verified the exact patched staged graph then removed all 20 files from libs/Math/IBFS and libs/Math/TRWS plus SceneDensify.cpp, SceneRefine.cpp and SceneTexture.cpp before CMake. Retained 3274-file staged tree fingerprint e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489 (path/content only, includes VCG/Eigen, ignores rattler-generated root files). Reduced ReconstructMesh built, named-input link-map guard passed, installed and fresh tests passed, and limited package audit passed. Originals were fetched before removal; no source/archive/binary was uploaded. No independently reproducible distribution archive, full source/notice assessment or legal clearance exists; removing named paths does not prove no restricted code elsewhere. All acceptance criteria remain open. See research/open-components-license-review.md.
<!-- SECTION:NOTES:END -->
