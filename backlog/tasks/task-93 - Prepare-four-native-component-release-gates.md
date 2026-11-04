---
id: TASK-93
title: Prepare four native component release gates
status: In Progress
assignee: []
created_date: '2026-11-04'
labels:
  - packaging
  - release-readiness
dependencies: []
ordinal: 93000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Collect current bounded native build, fresh retest, package audit and source-manifest evidence for dem2mesh, renderdem, poissonrecon-odm and mvs-texturing-odm.
- [x] #2 Prepare a component-by-component decision record identifying each of the four release gates, unresolved evidence and the exact candidate identities.
- [ ] #3 Resolve outstanding provenance, source completeness, license and release-candidate validation issues and obtain explicit owner decisions on each exact candidate before any publication.
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:NOTES:BEGIN -->
Temporary hosted run 41840541554 passed the four production recipe builds, packaged and fresh tests, audits, source bundling and verification of each source manifest's listed files. No artifacts were uploaded or retained. See research/four-component-release-gates.md for candidate hashes, limitations and component-specific unresolved decisions. The temporary build included its harness in the source bundle, so final-commit source checks must be repeated. Existing source/license gates are false and must not be changed based on this evidence alone. Publication and merge of an approval require separate owner authorization.
<!-- SECTION:NOTES:END -->
