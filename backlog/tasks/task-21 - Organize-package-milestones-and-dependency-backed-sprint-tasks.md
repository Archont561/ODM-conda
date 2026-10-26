---
id: TASK-21
title: Organize package milestones and dependency-backed sprint tasks
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-26 21:13'
labels:
  - planning
  - backlog
dependencies:
  - TASK-50
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User requested a milestone per package and chose one coordinating Sprint task per milestone. Cover all 13 packages in the existing plan; reuse existing work IDs and criteria, add missing starter validation and per-package evidence review, and make upstream delivery dependencies explicit without granting release approval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 13 packages have distinct, undated milestones with exactly one unassigned Sprint coordinator and concrete prerequisite work tasks.
- [x] #2 Original IDs, completion states and acceptance criteria are preserved; existing dependency constraints remain reachable, independent native engines remain parallel, and ODM/NodeODM depend on upstream package readiness rather than missing or cyclic work.
- [x] #3 CLI-owned navigation and local skill guidance explain the hierarchy; automated checks reject unknown milestones, empty sprint dependencies and completed sprints with unfinished prerequisites, and source/ignore coverage includes milestone files.
- [x] #4 Shared checks and both recipe renders pass; immutable native/tool/license/workflow inputs and all false release gates remain unchanged, with no generated export, native rebuild, project commit, push or publication.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use the pinned CLI for all work/milestone mutations. Snapshot original work and protected inputs, create one sprint gate per package with implementation/validation plus independent review dependencies, then assign milestone membership. Strengthen ODM/NodeODM and shared owner/platform sequencing while preserving existing constraints transitively. Add a failing milestone-reference regression and generic hierarchy checks, update the existing Backlog plan/owned guidance, run the shared gate, verify all associations/acyclic dependencies/source/ignore/protected hashes, close only the organization task, and clean temporary outputs.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created thirteen CLI-managed package milestones m-0..m-12, one unassigned/undated Sprint coordinator per package, thirteen evidence-review tasks and two missing starter validation tasks. Existing work IDs, AC/status histories and original dependency constraints are preserved (transitively through gates). TASK-2 belongs to fpcfilter; TASK-3 is shared. TASK-13 requires all eleven native Sprint gates plus TASK-3, TASK-14 requires the ODM gate, and shared owner/platform work retains original prerequisites plus appropriate starter/ODM gates without cycles. Independent native engines remain parallel. Updated doc-1 with clickable milestone/Sprint/work/review mapping plus owned agent/session/Backlog/README navigation. Unknown-milestone regression failed red before new checks; generic validation also rejects empty or non-own work Sprint dependencies, missing/duplicate active gates and completed Sprints with unfinished dependencies. Main and fresh maintained-source-only non-Git checks passed 48 Python + 4 Bun tests, metadata/workflow/ShellCheck/skill checks and both renders; source inclusion, real Git-ignore behavior, local links, original status/ACs and prerequisite reachability were verified. Fresh-source testing exposed an older Convco test-fixture defect and missing-config fallback, isolated and fixed in TASK-50, with a correction appended to TASK-20. Only the two task guards and their expected strings changed beyond the planned milestone/check/navigation work; all dependency/source/native/notice/workflow identities and false release gates are unchanged. All forty package-associated work items remain To Do. No dates, assignees, native builds, ZIP, project commits, remote changes or publication; session output/cache cleaned after verification.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Milestone → one dependency-backed Sprint → concrete work/review hierarchy is in place for all thirteen packages. Forty package-associated items remain To Do; shared legal/owner/platform work stays separate. Original AC/statuses and prerequisite constraints are preserved. All 52 tests and both renders pass in the main and fresh-source trees; graph/source/pin checks pass. TASK-50 fixed the checkout-dependent Convco fixture and missing-config fallback discovered by export verification. No actual package completion, publication approval or native rebuild is implied.
<!-- SECTION:FINAL_SUMMARY:END -->
