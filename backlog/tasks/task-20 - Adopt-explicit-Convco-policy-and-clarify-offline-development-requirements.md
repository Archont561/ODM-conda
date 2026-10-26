---
id: TASK-20
title: Adopt explicit Convco policy and clarify offline development requirements
status: Done
assignee: []
created_date: '2026-10-26 20:37'
updated_date: '2026-10-26 21:13'
labels:
  - tooling
  - offline
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User approved adopting Convco configuration now and asked whether offline development needs Pixi/conda-forge packages. Add .config/convco.yml with shared stdin/history commands, retain independent native versions and release gates, and distinguish already-declared tools from cached/portable offline payloads. Do not add a sandbox publisher or unrequested dependency upgrades.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An attributed explicit Convco policy lives under .config and is required packaging source; both commit-msg stdin and PR history tasks select it explicitly, with no root .versionrc stub or automatic version/release task.
- [x] #2 Pinned Convco validates supported types/scopes and rejects invalid types/scopes/messages for stdin and real Git ranges. Scope matching is anchored: a probe showed the reference unanchored pattern accepted partial invalid scopes.
- [x] #3 Existing conda-forge tools, separate Bun/npm payloads, host prerequisites and native build/source-cache boundaries are documented honestly; any offline check is scoped to the provisioned machine, not a clean-machine/full-native guarantee.
- [x] #4 Shared checks and real hook checks pass; dependency/source/notice/workflow identities and false release gates are preserved, and generated output/caches are removed without ZIP or publication.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use the agreed public seams: Pixi task definitions/required-source selection and the real pinned Convco stdin/Git-range CLI. Write a failing policy-wiring test, add attributed config and shared flags, verify allowed/rejected commits and missing-config failure, run common/hook checks, and separately exercise/document warm-machine offline readiness. No package upgrades or automatic transport publishing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added attributed .config/convco.yml, explicit shared flags for commit-lint and commits, required source inclusion and static policy checks. Preserved reviewed type/changelog groups and configured ODM-conda identity. Anchored scopeRegex after a pinned Convco 0.7.2 probe showed the unanchored reference accepted partial matches in bad scopes. No version/release-bump keys/tasks or root config stub were added. The policy-wiring regression failed before implementation and passed afterward. Five real-tool tests cover shared flags/source, valid messages, invalid types/scopes, missing-config refusal and real Git ranges in disposable fixtures. pixi run check passed 44 Python + 4 Bun tests and both recipe renders; the installed commit-msg hook accepted a good message and rejected a spaced scope, and unfiltered pre-push passed. Both named environments installed with frozen lock identity. With child IP/non-Unix socket creation and io_uring denied by seccomp, pixi run --offline --locked check plus real Backlog reads passed on this already-provisioned host (telemetry disabled for the test). Offline guide doc-9 distinguishes existing conda-forge tools/Bun/npm data, host Git/shell/Pixi, native dependency/source caches and a future portable transport. No cold-cache/machine-relocation/native-offline guarantee or sandbox publisher is claimed. Dependency/source/notice/workflow hashes are unchanged; only two Pixi task commands changed. Release-check still refuses false gates. No project commit, native rebuild, ZIP, remote push or upload; session-generated output/cache is removed after validation.

Correction discovered during TASK-21 and resolved by TASK-50: the original missing-policy negative check ran without a Git repository and was a false positive. In a valid Git fixture, Convco 0.7.2 silently falls back when --config is missing. Both tasks now explicitly test policy-file existence, and stdin/history tests use isolated Git fixtures. Full and fresh-source checks pass; earlier type/scope/history and offline observations otherwise retain their stated scope.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Explicit Convco policy adopted under .config and used by hooks/PR history checks. All 48 tests, both recipe renders and real hook checks passed, including scoped/type/missing-config/Git-range cases. Warm-machine offline checks and Backlog reads passed with child network sockets blocked; offline provisioning limits are documented in Backlog doc-9. No new package dependencies/transport or automatic native version/release logic was introduced. Source/tool/notice/workflow identities and blocked release gates are preserved; generated output cleaned.
<!-- SECTION:FINAL_SUMMARY:END -->
