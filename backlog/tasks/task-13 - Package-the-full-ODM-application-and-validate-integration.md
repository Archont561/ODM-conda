---
id: TASK-13
title: Package the full ODM application and validate integration
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - opendronemap
milestone: m-11
dependencies:
  - TASK-24
  - TASK-27
  - TASK-29
  - TASK-31
  - TASK-33
  - TASK-35
  - TASK-37
  - TASK-39
  - TASK-41
  - TASK-43
  - TASK-45
  - TASK-3
priority: high
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/ODM
Reference in selected ODM build: 47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45
Next work: Package application files/launcher; replace SuperBuild path assumptions and consume validated component packages.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
- [ ] #4 The application consumes packaged components rather than rebuilding SuperBuild; resources, imports, paths and the odm launcher work after relocation.
- [ ] #5 A suitably licensed end-to-end drone dataset succeeds in a fresh environment; unsupported features are explicit.
<!-- AC:END -->
