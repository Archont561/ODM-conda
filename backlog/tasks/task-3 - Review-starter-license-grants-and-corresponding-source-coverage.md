---
id: TASK-3
title: Review starter license grants and corresponding-source coverage
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 09:46'
labels:
  - license
  - release
dependencies: []
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Both component release acknowledgements are intentionally false. Review GPL version-choice grants, the dem2points BSD parser, FPCFilter bundled MIT/BSD headers, installed MIT test code, dependency obligations, and the durable source URL. Successful compilation and archive generation are not legal certification. See the component license inventory and review checklist in Backlog doc-6.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The applicable -only/-or-later expressions and all required notices have been explicitly reviewed.
- [ ] #2 The source set matches each binary, including modified/bundled code and build scripts, and any required dependency source is covered.
- [ ] #3 Maintainer approval is recorded before any release flag is enabled; unresolved issues remain open.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Review the pinned source grants and notice bytes for both starter components. Reconcile each expression with upstream grant language, inspect the complete staged source and actual build graph, document dependency-source obligations and any unresolved legal/maintainer questions. Keep all release checks false; do not represent this as legal advice or owner approval.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-26 preliminary source-level review (not legal advice or maintainer approval): fetched the pinned dem2points and FPCFilter codeload archives and verified their SHA256 values against recipes/components.json (dem2points b5d87bcafd52fd4c52f5c8828086f2ea34338742ae293cbd21bde1fd55b9fa67; FPCFilter fb303e298ad5e5f246a20095ce0992b97e0cf6605387df5fd3e2d930516025a8). Both root LICENSE files contain GNU GPL Version 3 text, but the project sources do not establish a grant selecting GPL-3.0-only versus GPL-3.0-or-later; the standard GPL text’s generic version-choice language is not evidence of the authors’ choice. Keep the current conservative GPL-3.0-only expressions pending explicit maintainer confirmation. The dem2points parser header contains the BSD-3-Clause notice; FPCFilter cxxopts.hpp/json.hpp contain MIT notices and nanoflann.hpp contains BSD-2-Clause; the packaging builder stages these headers’ first comments plus each root license and the packaging MIT notice. FPCFilter’s test tree contains additional bundled test materials; it is excluded from the current build via BUILD_TESTING=OFF but retained in the full corresponding-source archive. Source staging was regenerated deterministically: dem2points bundle SHA256 9271c67109881484f45c09f07e4fd73026d1bee5e580dfb930dc7f66da8373d6; FPCFilter bundle SHA256 d27c4487ef70e44e0790fd009be16f05cb36a8ec05a002ddabf5c6baeaffe595. The current recipes declare libgdal-core for dem2points and libgomp for FPCFilter, but external dependency source/redistribution obligations and exact shipped dependency graph still require maintainer review; no fresh binaries are available to match. The source URL template points to GitHub release assets that have not been published, so durable public availability has not been demonstrated. All release acknowledgements remain false; TASK-3 criteria remain open for maintainer/legal review and current-artifact correspondence.

2026-10-27 update (fpcfilter portion only): the project owner granted full release approval for fpcfilter 0.2 build 1 - local patch 0001, the modified-source notice, the GPL-3.0-only AND BSD-2-Clause AND MIT expression and the b1 source bundle are owner-confirmed, and all four fpcfilter release gates are now true (TASK-2 closed; doc-10 sections 5-6 record the decision). That is an owner policy approval, not legal certification. Still open in this task: the dem2points expression and gates, dependency source/redistribution obligations for both components, and demonstrating durable public availability of the source URL - the fpcfilter b1 release itself will publish source-fpcfilter-0.2-b1.tar.gz as the persistent release asset, which resolves durability for fpcfilter once it lands.
<!-- SECTION:NOTES:END -->
