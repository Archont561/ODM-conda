---
name: session
description: Start, scope, validate and close a local ODM packaging work session. Use at session start, when choosing work, and when reporting completion or blocked work.
---

# ODM session loop

1. Inspect `git status` and the user's requested scope. Do not reset or overwrite
   unrelated changes. This scaffold is task-scoped by default, not an automatic
   sprint/version/release train.
2. Bootstrap only what is needed:
   ```bash
   pixi install --locked
   pixi install --locked -e agent-tools
   pixi run -e agent-tools bun-install
   ```
3. Read `.agents/skills/backlog/SKILL.md`, then survey existing work:
   ```bash
   pixi run -e agent-tools bunx backlog task list --plain
   ```
   Package milestones use one dependency-backed Sprint gate each (Backlog doc-1).
   Execute a ready concrete prerequisite, not a Sprint as a substitute for work.
   Read the relevant task with `task TASK-N --plain`. Choose or create one bounded
   task, then record status, acceptance criteria and an implementation plan with
   the CLI before implementation. Ask when the requested scope or test seam is unclear.
4. Use the packaging/release skill for those domains. For behavior changes agree
   the test boundary, use the managed TDD skill, then a separate focused refactor.
   Do not fold unrelated cleanup into the task.
5. Run `pixi run check`. When native inputs change, also build, reinstall-test,
   audit and source-bundle the affected component. A skipped/unavailable native
   runner is blocked evidence, not a passed test.
6. Record evidence, remaining limitations and acceptance-criterion results through
   Backlog's CLI. Mark Done only when the stated criteria are actually satisfied.
   Keep maintainer-only actions open. Commit/push only when requested or authorized;
   use a Conventional Commit if committing.
7. End with a short user-facing result, tests and open task IDs. Do not create a
   new hand-off/roadmap Markdown file or force a release to close the session.

Local hooks are convenience checks; they do not replace CI, license review or
release authorization. Never update managed skills or either lock incidentally.
