---
id: TASK-1
title: 'Adopt pixi-sandbox tooling, Backlog and skills'
status: Done
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 19:20'
labels:
  - tooling
  - agents
  - backlog
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the scaffold's hand-maintained roadmap/planning documents with Backlog.md and scoped agent skills. Reference: Archont561/pixi-sandbox commit 1903b088a0896126dee82e2a8b6b007942303ffc. Preserve the existing channel archont561/archont561, exact native source pins, and false publication acknowledgements. Bun agent tooling is isolated from the Python packaging environment because their ICU requirements cannot coexist.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Backlog.md is Bun-locked and is the sole maintained source for future work, acceptance criteria, dependencies, notes, and project decisions.
- [x] #2 Managed skills are installed with pinned source refs and verified content hashes; repo-specific skills route packaging and release work.
- [x] #3 Convco, Lefthook, Actionlint plus ShellCheck and thin Pixi-driven checks work locally without weakening publishing isolation.
- [x] #4 Source bundles and the downloadable scaffold include Backlog/skills/tool locks but exclude node_modules, caches, and Git internals.
- [x] #5 Offline tests, real tooling smoke checks, fresh-layout validation, and publication refusal pass; native limitations and unrun remote steps remain explicit.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Inspect the pinned reference; preserve native packaging and isolated publication; implement and validate the tooling and Backlog/skills migration.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented exact hooks/linter pins and thin shared Pixi gates; migrated planning to CLI-created Backlog records; installed and hash-checked three pinned managed skills plus four local ODM skills with imported MIT notices. pixi run check passed 33 Python + 4 Bun tests. Real Lefthook positive/negative commit-msg and pre-commit/pre-push smoke checks passed. Existing native artifacts were retested and audited, not rebuilt. Publisher job and component source/release metadata are unchanged; release-check refused all four false gates. Archive preflight/source repeatability remains pending; see doc-5.

Archive preflight passed: deterministic 81-file source ZIP; genuinely fresh locked extraction passed the full common gate without Git, then actual Backlog/skills CLI reads after local init. Both native corresponding-source bundles reproduced identical hashes and include Backlog/skills/locks without dependency/cache/Git state. Local FPC staging passed all strict checksums. No native rebuild, hosted CI, remote push/OIDC/upload, legal sign-off or full ODM/NodeODM validation was claimed. See doc-5 for the complete evidence and limitations.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the local tooling and work-state migration: Backlog replaces the parallel roadmap/issues docs; four ODM-specific skills route work and three CLI-installed upstream skills retain pinned refs, verified hashes and MIT notices. Convco/Lefthook/Actionlint+ShellCheck/Taplo share Pixi entry points with thin CI, while the credentialed publisher is unchanged. All five migration criteria verified locally (33 Python + 4 Bun tests, real hooks/CLIs, fresh extraction, repeatable source archives, staging and refusal checks). Existing native artifacts were retested/audited, not rebuilt. Both components retain all four false human release gates; TASK-2/TASK-3/TASK-13/TASK-15 and other future work remain open.
<!-- SECTION:FINAL_SUMMARY:END -->
