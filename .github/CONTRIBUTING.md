# Contributing

Use Backlog.md for planned work, acceptance criteria, dependencies and implementation
evidence. Do not add a parallel roadmap, hand-off report or manual known-issues list.
For agents, [AGENTS.md](../AGENTS.md) is the entry point; contributors can read the same
scoped skills without needing a particular agent tool.

## Set up and check

On Linux x86-64 with Git and Pixi 0.82.0 (initialize Git first if using the ZIP):

```bash
pixi install --locked
pixi install --locked -e agent-tools
pixi run hooks-install
pixi run check
pixi run -e agent-tools bunx backlog task list --plain
```

Task/decision operations: [.agents/skills/backlog/SKILL.md](../.agents/skills/backlog/SKILL.md).
Component work: [.agents/skills/odm-packaging/SKILL.md](../.agents/skills/odm-packaging/SKILL.md).
Release review: [.agents/skills/release-review/SKILL.md](../.agents/skills/release-review/SKILL.md).

Hooks are local convenience checks. CI repeats the shared task entry points;
native changes also require build, fresh installed tests, audit and source bundles.
Ordinary PR checks render recipes but do not compile the native tools.

## Commits and dependencies

Use Conventional Commits, for example `fix(fpcfilter): correct radius sampling`.
Both commit-msg stdin validation and PR commit ranges explicitly use
`.config/convco.yml`. Supported types are feat/fix/perf/refactor/docs/build/ci/test/
chore/style; optional scopes use alphanumeric segments separated by `-`, `_` or `/`. Conventional Commits do not automatically bump an upstream component version.

Change exact direct tool pins and regenerate `pixi.lock` / `bun.lock` deliberately.
Normal bootstrap/CI uses frozen locks, never a floating update. Managed skills must
be updated through the locked skills CLI at reviewed full commit refs, with their
source licenses retained; see [.agents/NOTICE.md](../.agents/NOTICE.md).

Application dependencies belong in recipes, not Pixi's repository environment.
Do not download undeclared sources or install pip/npm dependencies during a native
recipe build. Update a component's manifest and recipe together, increment its
build number if repackaging the same version, and never replace published artifacts.

## Rights and release acknowledgements

Copied upstream code/patches retain their applicable licenses, not the repository's
MIT label. Inventory per-file, bundled/header-only code and asset/model rights.
Review [the Backlog licensing guide](../backlog/docs/guides/doc-6%20-%20Licensing-and-source-distribution-checklist.md); reset affected human gates after source,
patch, ABI, source-staging, fixture-coverage or licensing changes. Do not flip gates
just to pass CI, and do not publish merely because a task is marked Done.

## Offline development

Provision both locked Pixi environments and Bun dependencies while connected.
For a prepared machine, `pixi run --offline --locked check` is a useful readiness
check, but Pixi's switch does not firewall child processes. Package caches, host
Git/shell/Pixi and native build/source inputs have separate requirements. See the
[offline provisioning guide](../backlog/docs/guides/doc-9%20-%20Offline-development-tooling-and-provisioning-boundaries.md) for scope and limitations.
