---
id: TASK-17
title: Remove obsolete exports and root docs
status: Done
assignee: []
created_date: '2026-10-26 19:39'
updated_date: '2026-10-26 19:45'
labels:
  - maintenance
  - tooling
dependencies: []
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User requested removing the ZIP, root docs, build output and other obsolete files/paths or ignoring them. Preserve required notices, immutable source/tool locks and Backlog/skills; move necessary release/licensing guidance into CLI-managed Backlog docs. Do not publish or rebuild native artifacts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Needed licensing, publishing and historical validation records are preserved in Backlog and all active navigation uses their new locations.
- [x] #2 Root docs, delivered ZIPs, generated build/audit/source/staging output and prior research scratch files are removed without deleting required notices, source, locks or installed ignored tools.
- [x] #3 Ignore and source-allowlist rules exclude obsolete docs and generated exports while keeping backlog/docs, tasks, skills and locks versionable.
- [x] #4 Shared checks and cleanup regression tests pass; release gates and credentialed publisher remain unchanged; generated output is removed again after validation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Move remaining root docs through the Backlog CLI, preserve the native audit snapshot as archived evidence, add failing exclusion/ignore tests, remove obsolete source paths and fix navigation, tighten .gitignore, run the shared checks, then delete regenerated outputs and scratch exports. Keep installed tools ignored and all publication gates unchanged.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed the delivered ZIP and prior research scratch tree, root docs, native output, audit reports, source bundles and staging caches. Preserved needed guidance through the Backlog CLI: doc-6 licensing, doc-7 publishing, doc-8 archived native validation including the original JSON artifact snapshot. Updated active README/contribution/agent links; root docs are obsolete and no longer in the source allowlist. Added archive/source-exclusion and real git check-ignore regression tests; each failed before its fix. The full shared gate passed 36 Python plus 4 Bun tests, metadata/skill hash checks, Actionlint with ShellCheck and both recipe renders. Removed rendering output and caches again after checks. Exact source/tool locks, required notices, managed skill content and credentialed publisher are unchanged; four review gates remain false and release-check correctly refused publication. Local .pixi/node_modules are retained but ignored. No native rebuild, Git commit, remote push or upload performed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Repository cleanup complete: obsolete docs/ and generated ZIP/native/audit/source/staging/research files removed; necessary guidance/evidence preserved in Backlog. Anchored ignore rules protect backlog/docs and locks while excluding obsolete/generated paths. Source packaging omits root docs and generated archives. All 40 tests and the common gate passed; final local output cleaned after validation. Publishing remains blocked and source identities/credential isolation are unchanged.
<!-- SECTION:FINAL_SUMMARY:END -->
