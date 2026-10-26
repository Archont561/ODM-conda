---
name: backlog
description: Manage ODM work, acceptance criteria, dependencies, plans and implementation evidence with Backlog.md. Use for task IDs, planning, progress, known issues or architectural decisions.
---

# Backlog is the work-state source of truth

Use the locked CLI, not manual task-file edits:

```bash
pixi run -e agent-tools bunx backlog task list --plain
pixi run -e agent-tools bunx backlog task TASK-2 --plain
pixi run -e agent-tools bunx backlog search "source archive" --plain
```

`bunx` first runs `bun install --frozen-lockfile`, then `bun x --bun`. Bun is in an
isolated environment because its ICU requirement conflicts with the packaging
Python environment. No system Node or bare bunx shim is assumed.

Read commands require `--plain` or `--json` for agents. Do not launch the terminal
board or browser in a non-interactive tool call. Use live `--help` for the pinned
CLI's actual flags; for example, documents use `doc update`, not `doc edit`.

## Task lifecycle

```bash
pixi run -e agent-tools bunx backlog task create "Package a component" --ac "Pinned sources" --ac "Installed test passes" --labels packaging
pixi run -e agent-tools bunx backlog task edit TASK-N --status "In Progress" --plan "One bounded approach"
pixi run -e agent-tools bunx backlog task edit TASK-N --append-notes "Observed evidence and command results"
pixi run -e agent-tools bunx backlog task edit TASK-N --check-ac 1
pixi run -e agent-tools bunx backlog task edit TASK-N --status Done --final-summary "Verified outcome and remaining limitations"
```

Use task dependencies for the integration order. A failed upstream feature is an
open bug task, not an unchecked note hidden in a static roadmap. Do not assign
someone, create a milestone/release, or claim maintainer approval without authority.
Task completion does not toggle the package's release checks.

## Package milestones and sprint gates

The owner has requested one package milestone and one Sprint coordinator per
package. The mapping lives in Backlog doc-1; milestone files live in
`backlog/milestones`. Read through the CLI:

```bash
pixi run -e agent-tools bunx backlog milestone list --plain
pixi run -e agent-tools bunx backlog task TASK-24 --plain
```

Use `milestone add` and task `--milestone` only with owner-authorized scope.
Milestone membership plus actual task `dependencies` represents the hierarchy;
do not duplicate or renumber the existing work to fake a parent tree. Sprint
tasks carry the `sprint` label and depend on concrete implementation/validation,
independent evidence review and applicable shared prerequisites. Choose a ready
leaf task for execution; do not close a Sprint with unfinished dependencies.

`task edit --depends-on` replaces the entire dependency list. Read/merge the
existing constraints and recheck acyclicity and upstream reachability rather than
silently dropping prerequisites. Native engines remain parallel; ODM depends on
native package gates, NodeODM on the ODM gate, and shared owner/platform work stays
outside individual milestones. Do not infer dates, assignees, release authority
or automatic native-version bumps from a Sprint or milestone.

## Plans and decisions

Project plans and ADRs live under `backlog/docs`, managed by the CLI:

```bash
pixi run -e agent-tools bunx backlog doc list --plain
pixi run -e agent-tools bunx backlog doc view doc-3 --plain
pixi run -e agent-tools bunx backlog doc create "A bounded design" --path plans --plain
pixi run -e agent-tools bunx backlog doc update doc-N --content "The actual decision, evidence and consequences"
```

This pinned CLI can update project docs but has no decision-edit subcommand, so
maintained ADRs use `doc create --path adr` and `doc update`. Do not invent flags.
Use actual newlines for multiline arguments and quote literal backticks; never
put shell-generated command substitution into task content. Use subprocess argument
arrays when automating the CLI. Auto-commit, remote operations and branch probing
are disabled; keep them disabled unless the owner chooses otherwise.

The README is navigation; source pins and legal/validation records remain their
own maintained data. Do not move license notices into ephemeral tasks or delete them.

Pattern adapted from Archont561/pixi-sandbox 1903b08; see `.agents/NOTICE.md`.
