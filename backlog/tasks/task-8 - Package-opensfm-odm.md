---
id: TASK-8
title: Package opensfm-odm
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - opensfm-odm
milestone: m-6
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/OpenSfM
Reference in selected ODM build: c5328439465e6ace011f39077d1077d7b1cdd65d
Next work: Python/C++ recipe, Python/NumPy ABI pins, vendored sources, imports, and an SfM dataset test.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
<!-- AC:END -->
