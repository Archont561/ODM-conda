---
id: doc-5
title: Backlog skills and tooling refresh validation
type: other
created_date: '2026-10-26 19:18'
updated_date: '2026-10-26 19:39'
---
Historical validation record: the generated ZIPs, local native artifacts, root docs and research scratch described here were subsequently removed by TASK-17. Source, notices, tasks and skills remain maintained; original artifact hashes are archived in doc-8.

# Local tooling refresh evidence — 2026-10-26

Scope: local scaffold/source delivery only, Linux x86-64. No GitHub/Prefix
repository, authorization, channel settings or public artifact was created.

## Verified before archive preflight

- Backlog.md 1.53.0 and skills 1.7.2 were installed from an exact private Bun
  manifest and frozen lock. Backlog initialized with its actual CLI; 16 tasks
  and five project docs were created/updated through it, not hand-seeded IDs.
- Four local ODM skills route sessions, Backlog, packaging and release review.
  Three managed skills were installed through skills 1.7.2 at full commit refs.
  CLI-generated locks and upstream MIT licenses are retained. Bun independently
  reproduced all three content hashes with JavaScript localeCompare ordering.
- The component roadmap was removed from components.json. Architecture and
  known-issues planning moved to Backlog; necessary legal/publishing and initial
  native validation records remain. No full ODM or NodeODM package is implied.
- Exact direct tooling pins: Convco 0.7.2, Lefthook 2.1.14, Actionlint 1.7.12,
  ShellCheck 0.11.0, Taplo 0.10.0. Default and agent-tools locked installs passed.
  Bun's Conda package is 1.3.11; executable reports 1.3.11-canary.1 (7e5d2979).
- pixi run check passed: 33 Python tests, four Bun tests, Python/TOML/manifest/
  Backlog/provenance checks, real skill hashes, Actionlint with ShellCheck, and
  both recipe renders. Hash checks, task-dependency cycles, source exclusions,
  staged syntax, hook filters and workflow policy have regression coverage.
- Lefthook config validation and actual staged pre-commit jobs passed. The
  commit-msg job accepted a conventional message and rejected a bad message.
  A forced pre-push run executed all four unfiltered jobs, sequentially. These
  were local tool invocations, not an actual commit or push to a remote.
- Backlog task/doc reads passed. skills list --json was parsed as actual JSON;
  frozen dependency installation is silent to keep structured stdout clean.
- Both EXISTING native artifacts were reinstalled/tested in fresh runtime
  environments and re-audited successfully. Their hashes and native component
  metadata are unchanged from the archived artifact snapshot in Backlog doc-8. This tooling
  refresh did not rebuild the native binaries or fix the TASK-2 upstream bug.
- fpcfilter-v0.2-b0 release-check correctly refused all four false human gates.
  The credentialed publisher job is semantically unchanged from the original
  scaffold: no checkout/project execution, source before binary, scoped OIDC.

## Archive preflight

- An 81-file maintained-source ZIP passed CRC/content/exclusion checks and a
  byte-identical repeat-generation comparison. Git internals, node_modules,
  Conda prefixes, caches, binaries and local Backlog preferences are excluded.
- A genuinely fresh extraction installed both environments with committed locks.
  Its full pixi run check passed WITHOUT a Git root (33 Python + four Bun tests,
  exact managed hashes, metadata, Actionlint/ShellCheck and both renders).
- After git init in that disposable extraction, real Backlog reads succeeded;
  the skills CLI listed all seven skills and its stdout parsed as JSON.
- Both regenerated native source bundles were independently built twice with
  identical per-state hashes. Maintained Backlog/skills/locks were present;
  dependency trees, caches and Git internals were absent.
- Refreshed local FPCFilter release staging passed strict SHA256SUMS checks for
  binary, source bundle and audit. Nothing was uploaded.
- The extracted scaffold also refused fpcfilter-v0.2-b0 with all four human gates
  false. The final download is regenerated after these CLI-owned task/doc notes;
  hashes are kept outside its own source tree to avoid a self-referential digest.

TASK-1 closes only the tooling migration. Remaining scientific, legal, platform,
integration and owner-controlled publishing tasks are not marked complete.

## Still not verified or authorized

No hosted GitHub Actions run, actual remote push, OIDC exchange, public upload,
complete license/source-completeness sign-off, minimum-glibc host, non-Linux target,
CUDA, full ODM/NodeODM integration or real drone dataset execution. All four
human release gates remain false for both starters. TASK-2, TASK-3, TASK-13 and
TASK-15 (and other future-component/platform work) remain open.
