# Working in ODM-conda

Start with `.agents/skills/session/SKILL.md`. Backlog.md, not a parallel roadmap
or session report, owns future work, acceptance criteria, dependencies and progress.

Package work is organized as Backlog milestone → Sprint gate → prerequisite tasks.
Read the local Backlog skill and choose concrete, dependency-ready work; a Sprint
completion never implies automatic versioning or permission to publish.

Routing:

- Tasks/notes/decisions: `.agents/skills/backlog/SKILL.md`.
- A native component recipe: `.agents/skills/odm-packaging/SKILL.md`.
- Publication or a release acknowledgement: `.agents/skills/release-review/SKILL.md`.
- Behavior changes: managed `tdd`, then a separate managed `refactor` pass.
- Agent instructions: managed `writing-for-agents`.

The managed skills are committed copies installed by the pinned skills CLI.
`skills-lock.json` records their source commits and content hashes. Never edit a
managed skill in place or auto-update it during CI. Local ODM skills are intentionally
not entries in that external-source lock. Apply guidance with available tools;
do not claim to invoke a tool/optional skill that is not installed.

`pixi run check` is the cheap local/CI gate. Native build/test/audit commands are
separate. Use the default Pixi environment for Python/native tools and
`pixi run -e agent-tools bunx ...` for Backlog/skills. Both tool locks are committed.

Do not replace executable source/version/license metadata with task state.
`recipes/components.json` owns implemented recipes; Backlog owns proposed work. Keep the
README and required license notices. Maintained legal/publishing guidance and
archived validation records live in `backlog/docs`; do not restore a root `docs/`
or keep generated ZIP/build/audit/staging files as repository source.

No session, completed task, conventional commit, or successful compiler run grants
permission to publish. Preserve the isolated OIDC publisher and human review gates.
Do not create remote repos, push, publish, or enable a gate unless authorized.
