---
id: doc-4
title: Thin workflows and isolated publishing
type: other
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 19:18'
---
# Accepted: thin Pixi-driven workflows with an isolated publisher

Status: accepted for this scaffold. Reference: pixi-sandbox 1903b08.

Use exact direct tool pins and committed Pixi/Bun locks. Hooks and CI call the
same Pixi tasks. Keep pre-commit cheap, Conventional Commit validation in commit-msg,
and sequential fail-fast pre-push checks without file-glob skips. Native compilation
is an explicit/manual CI gate, not a per-commit hook.

Workflow build/check steps are single Pixi task commands. Pull request runs may
supersede earlier runs for that PR; different main commits use distinct concurrency
keys. Release runs are never cancelled midway. No auto-bump infers an upstream
component version from packaging Conventional Commits.

The credentialed publish job is a reviewed exception to moving all shell code into
repository scripts: it must not check out or execute repository code just to make
YAML thinner. Retain minimal audited checksum/gh/upload commands there, explicit
narrow permissions, source-before-binary ordering, OIDC, immutable artifacts, and
false human release gates until approval. Local hooks remain convenience, not
server enforcement or legal approval.

The final checks workflow calls pixi run check and validates PR commit ranges with Convco. Pre-push reuses static, unit, agent-check and render tasks, sequentially and without changed-file filters. All component release runs share one repository/workflow concurrency group and are non-cancelling. A local structural comparison confirmed the credentialed publish job is unchanged from the initial scaffold; no project checkout or script was added there.
