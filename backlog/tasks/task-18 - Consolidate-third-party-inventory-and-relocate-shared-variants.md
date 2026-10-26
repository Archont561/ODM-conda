---
id: TASK-18
title: Consolidate third-party inventory and relocate shared variants
status: Done
assignee: []
created_date: '2026-10-26 19:58'
updated_date: '2026-10-26 20:00'
labels:
  - maintenance
  - packaging
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User approved removing the redundant root third-party inventory after consolidating useful information in Backlog doc-6, and moving the shared native toolchain configuration to recipes/variants.yaml. Keep that configuration versionable and preserve the current compiler/sysroot baseline and actual license notices.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Useful component, notice-handling and imported-skill inventory is preserved in Backlog doc-6; the redundant root THIRD_PARTY.md and active references to it are removed.
- [x] #2 recipes/variants.yaml is required source with byte-identical toolchain configuration; build, lint, source collection, tests and navigation use the new path.
- [x] #3 Source/tool pins, actual notice content, native recipes, isolated publishing workflow and all four false human gates remain unchanged.
- [x] #4 Regression and shared checks pass, including both real recipe renders; generated outputs are removed afterward without creating a ZIP or publishing.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Consolidate useful inventory through the Backlog CLI. Add a failing source-layout regression, move the unchanged shared variants into recipes, update all consumers/fixtures/navigation, remove the redundant inventory file, run the common gate and verify preserved hashes, then remove generated output and close only this maintenance task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Consolidated component license details, verbatim-notice handling and imported development-skill inventory into Backlog doc-6 through its CLI; retained unique OpenPointClass/texturing dependency-review cautions. Removed THIRD_PARTY.md only after confirming the component and notice-handling sections were preserved. Moved variants.yaml to recipes/variants.yaml without changing its checksum or compiler/sysroot values. Updated build and lint consumers, required source collection, fixture setup, Git-ignore regression coverage, README/local packaging skill, architecture doc-1 and license-review TASK-3. The new source-layout regression failed before the move and passed afterward; removing the new variants file fails required-source collection. pixi run check passed 37 Python plus 4 Bun tests and both real renders explicitly loaded recipes/variants.yaml. Source/tool locks, actual notices, managed skills, native recipes and all workflows retain their previous hashes. Four release gates remain false; release-check refused publication. No native rebuild, export ZIP, Git commit, push or upload. Generated render/cache output is removed after validation.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Approved root-layout cleanup complete. Third-party inventory is consolidated in Backlog doc-6; its redundant root file is deleted. Shared variants are required, non-ignored source at recipes/variants.yaml with identical content. Consumers and navigation updated; all 41 tests and both recipe renders passed. Notices, native source/tool pins, workflows and false release gates are unchanged. Generated output cleaned, with no new ZIP or publication.
<!-- SECTION:FINAL_SUMMARY:END -->
