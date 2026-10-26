---
id: TASK-19
title: Organize remaining movable root files into subfolders
status: Done
assignee: []
created_date: '2026-10-26 20:16'
updated_date: '2026-10-26 20:22'
labels:
  - maintenance
  - layout
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User clarified that subfolders within the existing Git repository are wanted, not separate repositories. Move the shared component manifest into recipes, Lefthook configuration into its supported .config discovery directory, and the contributor entry point into .github. Leave standard Pixi/Bun/skills manifests and locks, AGENTS.md, README, LICENSE and .gitignore at their expected root locations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 recipes/components.json and .config/lefthook.yml retain byte-identical configuration; .github/CONTRIBUTING.md retains its guidance with corrected relative links. No old root copies/stubs or separate repositories are introduced.
- [x] #2 Configuration loaders, checks, fixtures, source collection, active Backlog/skill references and navigation use the new locations; new paths remain versionable and local hook preferences are excluded from source.
- [x] #3 Real Lefthook auto-discovery/install and positive/negative commit-message checks work without a config environment override; the common gate and both recipe renders pass.
- [x] #4 Source/tool pins, notices, managed skills, native recipes/variants, workflows, existing channel and false release gates are preserved; generated outputs/caches are removed without ZIP, native rebuild, commit, push or publication.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verified pinned Lefthook 2.1.14 auto-discovers .config/lefthook.yml in a disposable Git fixture. Add source-layout regression, relocate the three files and update consumers/link bases, retain only tooling/convention entry points at root, verify discovery and hook behavior plus common checks, then remove regenerated output and close this maintenance task. Keep manifest recipe entries repository-root-relative.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Moved components.json to recipes/components.json and lefthook.yml to .config/lefthook.yml with identical hashes. Manifest recipe entries still resolve from repository root. Moved CONTRIBUTING.md to .github/CONTRIBUTING.md, changing only relative Markdown link bases. Updated loaders/diagnostics, hook-policy checks, required source collection, test fixtures/ignore coverage, README/agent skills and CLI-managed active Backlog docs 1/6/7. Standard Pixi/Bun/skills manifests and locks, README, AGENTS, LICENSE and .gitignore remain at root for discovery/conventions. Added a source-layout regression that failed before relocation, plus a real nested Lefthook auto-discovery regression using a disposable Git fixture with no environment override. pixi run check passed 39 Python plus 4 Bun tests and both real recipe renders. Real hook install/validation, staged pre-commit, installed commit-msg positive/negative and unfiltered sequential pre-push checks passed without LEFTHOOK_CONFIG or root stubs. A fresh maintained-source-only non-Git copy independently passed metadata, all 43 tests, skill hashes and Actionlint/ShellCheck. Local .config/lefthook-local.yml is ignored and excluded from source. Protected pins, notices, native recipes/variants and workflows have unchanged hashes; all release gates remain false and release-check correctly refused publication. No separate repositories, native rebuild, ZIP export, commit, remote push or upload. Generated caches/output removed after validation.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Subfolder organization complete: shared packaging metadata under recipes/, auto-discovered hook config under .config/, contributor entry point under .github/. No old root copies or stubs. Standard discovery/convention files remain at root. All 43 tests, both recipe renders, real hook smoke checks and fresh-source offline gates passed. Configuration/notice/tool identities and blocked publishing are preserved; generated output cleaned.
<!-- SECTION:FINAL_SUMMARY:END -->
