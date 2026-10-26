---
id: doc-3
title: Isolate Bun agent tools from packaging Python
type: other
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 19:18'
---
# Accepted: isolate Bun agent tooling from native packaging tooling

Status: accepted for this scaffold. Scope: development tooling only.

## Evidence

Conda Bun 1.3.11 requires ICU 75. Python 3.12.16 requires a SQLite build that
excludes ICU or requires ICU 78. A combined prefix failed dependency solving.
The reference pixi-sandbox is Rust/Bun-based and does not have this Python constraint.

## Decision

Keep packaging, testing, hooks and workflow linters in the default environment.
Use an agent-tools feature/environment containing Bun, with no default feature.
The JavaScript tool versions are exact package.json devDependencies locked by bun.lock.
Run Backlog.md and skills with pixi run -e agent-tools bunx, which first performs
bun install --frozen-lockfile, then bun x --bun. Do not assume a bunx shim or Node.

## Consequences

Python is not downgraded, agent tools are not Conda runtime dependencies of the
packaged C++ tools, and CI need not install Bun merely to compile a component.
Planning commands explicitly select agent-tools; frozen installation never updates
skills, task IDs or the committed skill lock automatically.

The frozen install is silent so --json CLI output remains machine-readable. The selected Conda Bun package is versioned 1.3.11 but its executable reports 1.3.11-canary.1 (7e5d2979); this exact build is locked and was smoke-tested. Full check/CI runs explicitly include the agent environment; a standalone native build need not invoke Backlog or skills.
