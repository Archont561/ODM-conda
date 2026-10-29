---
id: TASK-57
title: Resolve GDAL and PDAL ABI incompatibility in ODM MVP
status: In Progress
assignee: []
created_date: '2026-10-29 11:53'
updated_date: '2026-10-29 18:01'
labels:
  - integration
  - bug
dependencies: []
priority: high
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Disposable integration failed to solve dem2points build 0 with renderdem build 0: the former requires GDAL 3.11 and the latter requires PDAL 2.10, whose available conda-forge builds could not satisfy that GDAL version. Isolated reproduction: https://github.com/Archont561/ODM-conda/actions/runs/40868856018. Determine a common native ABI through versioned, genuinely rebuilt recipes, not by overriding metadata or loosening audits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Select an attainable shared GDAL/PDAL/OpenCV and compiler dependency set, including all MVP package requirements and exact artifact identities.
- [ ] #2 Build and individually retest/audit/source-bundle changed packages with appropriately bumped build versions; retain owner release gates.
- [ ] #3 Install all nine components into a fresh disposable environment, verify imports, binaries and relocation, and continue TASK-13 integration without publishing unapproved artifacts.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use a disposable CI solver to identify an attainable GDAL/PDAL/OpenCV runtime baseline; bump and rebuild the affected GDAL-dependent recipes with precise host/run ABI pins, reset changed release gates and keep published historical releases distinct. Validate rendered metadata and fixtures locally, request owner native multi-recipe build, then independently verify artifacts and assemble all nine components for integration. Never relax metadata to conceal ABI incompatibility.

Re-run disposable integration with independently verified coordinated artifacts and locally built research components. Capture the actual nine-component solve and run preflight, selected imports, launcher and candidate dataset only when prerequisites pass; record relocation and all blockers, retain no research or dataset artifacts.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
A disposable conda-forge solve of GDAL 3.13 with PDAL 2.10, Python 3.12, OpenCV 4.12, GDAL Python bindings and the selected integration dependencies failed: https://github.com/Archont561/ODM-conda/actions/runs/40904066709. A GDAL >=3.12,<3.13 solve of the same requested dependency set succeeded: https://github.com/Archont561/ODM-conda/actions/runs/40904165751, selecting libgdal-core 3.12.2 hc2c0581_0, libpdal-core 2.10.0 h9d23c72_0, libopencv 4.12.0 qt6_py312h52d6ec5_612, py-opencv 4.12.0 qt6_py312h598be00_612, Python-PDAL 3.5.3, and TBB 2023.1. This was dependency-only, not the nine actual artifact solve or native ABI proof. Candidate builds of dem2points, fastrasterfilter and odm-orthophoto now target GDAL 3.12 at host and run, bump build 0 to 1 and reset all four release flags. Published build 0 artifacts remain unchanged; dem2mesh stays outside MVP. Local pixi check passed (246 passed, 2 skipped); native dem2points build staged pinned source but failed conda-forge noarch repodata EOF before compilation; no new native package, test, audit or source bundle was produced. Owner must dispatch build.yml with the three changed recipes selected. Full integration solve, actual build/run ABI, legal/source review and owner gates remain open.

Owner run https://github.com/Archont561/ODM-conda/actions/runs/40906236704 on ec2cb925f7efbc84db5b16e8d92d3a8c83b55947 passed. Artifact 12912041865 ZIP SHA256 c217093dfc903c34b47e67620f012385f03ecbb777c82bbe990109eb5ac12623 independently inspected in https://github.com/Archont561/ODM-conda/actions/runs/40907763520: exactly dem2points, fastrasterfilter, odm-orthophoto build 1; each fresh retest, audit, 246 manifest hashes, pinned source and all declared upstream notice bytes passed. Package hashes respectively f7beed995be059343796b2d4727706a6fbf89a4bcd448a4a85ff0ca7c2c6da8d, 916027e4fcbd28da4cb39f164fa19b89b60714d43712866f023b0a7efed1e8af, 1ef443343ce49b8890d1a1915b54cb4c09efb3b17ad7998d4f23d091078bcaf6. Despite passing individual checks, minimal actual-artifact solve with RenderDEM build 0 FAILED: build 1 packages require libgdal-core >=3.12.4,<3.13 and RenderDEM requires libpdal-core >=2.10.2,<2.11. No combined installation happened. Proposed tighter shared GDAL >=3.12.2,<3.12.3 and PDAL >=2.10.0,<2.10.1 host/run pins, changing three recipes to build 2 and RenderDEM to build 1; these are unbuilt candidates. Four fresh owner native builds, audits, retests, source bundles and actual combined solve remain required; release gates remain false.

Owner run https://github.com/Archont561/ODM-conda/actions/runs/40908393516 at 75564b4c0f2869da40151783f54abd378be36a1d passed but independent inspection https://github.com/Archont561/ODM-conda/actions/runs/40908795526 established artifact 12910914634 ZIP SHA256 fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2 contains fastrasterfilter build 2, odm-orthophoto build 2 and renderdem build 1, NOT dem2points. Follow-up https://github.com/Archont561/ODM-conda/actions/runs/40908908691 verified 246 source manifest hashes each, upstream notice bytes, current audit and fresh retest. Package SHA256 respectively 52d42537b1ed1ba80a473e4540392d90f49f95e7e6dbb930445c9a3307f859dd, 093c55b75981239cb31dccaf66e44e9a4d2addcfe37e31950870451d2f0bb58f, 451a291036f9bf11c140464d088884ec8980051c5383a667b75d1be7637fea77. All three actual packages installed together with PDAL, Python-PDAL, GDAL and exiftool, selecting libgdal-core 3.12.2 hc2c0581_0, libpdal-core 2.10.0 h9d23c72_0, and Python 3.13 OpenCV; binary presence checked. This is not a four-component solve or ODM Python 3.12 integration. Owner must dispatch dem2points build 2; all gates remain closed.

Owner run https://github.com/Archont561/ODM-conda/actions/runs/40909632056 at d4e40293ff9627e21f806cf7f9a31226e969576d passed. Independent read-only https://github.com/Archont561/ODM-conda/actions/runs/40910163219 verified ZIP 12911564893 SHA256 2e6af14e3eaffa0631c59e875fa114b95376f17a1c7c7de4815e9fc3e7eefb87 contains dem2points build 2 only, package SHA256 f7077c2eb01f380503d2aa5203e20d78e824a1c4adceaa486f4cbaf22bee8cb0 and source bundle SHA256 9029351b2cccf4eeca82c580f7fab8c68f0f05410cae36ca003380c9d16a8ce8; verified 246 source manifest entries, upstream notice bytes, audit and fresh retest. Separately verified prior three artifact package hashes and installed all four with Python 3.12, Python OpenCV 4.12, PDAL and GDAL, selecting libgdal-core 3.12.2 hc2c0581_0 and libpdal-core 2.10.0 h9d23c72_0; checked binary presence. This is not functional testing in the combined prefix, nine-component solve, relocation, full ODM integration, complete license/source review or approval. Release gates stay closed.

Nine-package disposable installation and selected-import/executable preflight succeeded in run 40915195339 with GDAL 3.12.2, PDAL 2.10.0, gflags 2.2.x and Eigen 3.4 after genuine OpenSfM rebuilds. This demonstrates one solve, not complete relocation or dataset integration. Research artifacts were discarded; release gates remain closed.
<!-- SECTION:NOTES:END -->
