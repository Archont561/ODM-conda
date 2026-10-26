---
id: TASK-50
title: Fail closed when explicit Convco policy is missing
status: Done
assignee: []
created_date: '2026-10-26 21:10'
updated_date: '2026-10-26 21:13'
labels:
  - tooling
  - bug
dependencies:
  - TASK-20
type: bug
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fresh-source validation during TASK-21 exposed a checkout-dependent Convco test fixture. Correct Git fixtures then proved pinned Convco 0.7.2 silently uses defaults when --config names a missing file. Add an explicit file guard to both existing Pixi commit-check commands without changing pins or introducing a wrapper/version train; exercise stdin and real Git history in isolated fixtures.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both stdin and history entrypoints reject missing policy before invoking Convco; valid and invalid messages/ranges retain the reviewed behavior.
- [x] #2 Tests create their own Git fixtures and cannot pass negative cases merely because the source export lacks .git. Missing-config regression is demonstrated red in a valid Git repository.
- [x] #3 Only the two task commands and their checks/test fixtures change; dependencies/locks, Convco config, native inputs and release gates remain unchanged, and full/fresh-source checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use the currently failing real-Git missing-policy case, add a local test -f guard to each direct Convco task, execute the task shell definition in isolated Git fixtures, and verify real Pixi/hook plus source-export paths. No dependency upgrade or new wrapper.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Both missing-policy cases failed red in correctly initialized Git fixtures: Convco 0.7.2 returned success using its defaults. Added test -f .config/convco.yml && to both existing direct tasks and aligned their expected strings; no wrapper/dependency upgrade. Tests now initialize isolated Git fixtures and execute the task shell definition, with ranges passed as quoted positional arguments, so exported sources need no original checkout and negative cases cannot succeed only on a no-repository error. All five Convco cases, complete 48 Python + 4 Bun gate, both renders, fresh non-Git maintained-source checks and real installed commit-hook positive/negative checks passed. All non-task manifest fields, dependency locks, Convco configuration and native/release inputs are unchanged.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Commit checks now explicitly fail closed on missing policy for both stdin and history. Git-fixture isolation fixes export portability and prior false-positive negative checks. All 52 tests and both recipe renders pass in the main tree and fresh maintained source; no dependencies or native/release inputs changed.
<!-- SECTION:FINAL_SUMMARY:END -->
