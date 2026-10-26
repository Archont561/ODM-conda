# Agent-skill provenance and notices

Committed agent guidance is development tooling, not part of the installed native
component runtime. Root `LICENSE` does not replace upstream terms.

Managed copies installed with skills 1.7.2 (project-local, Codex target, `--copy`):

| Skill | Source commit | License copy |
| --- | --- | --- |
| tdd; writing-for-agents | mattpocock/skills @ 5beb35b040e3de97e54fa9e386d7e42d15c295c2 | licenses/mattpocock-skills-MIT.txt |
| refactor | github/awesome-copilot @ b1a00457c0b8794243883f387e7de71e88800e3e | licenses/github-awesome-copilot-MIT.txt |

`skills-lock.json` is manager-generated. Source-relative skill paths and original
content hashes are retained there. CI verifies the committed copies without
fetching or updating upstream skill content. See `licenses/manifest.json` for the
immutable source-license URLs. This is provenance/integrity checking, not a security audit.

Local `session`, `backlog`, `odm-packaging`, and `release-review` skills are maintained
here. Backlog/session routing and the tooling pattern are adapted from
Archont561/pixi-sandbox @ 1903b088a0896126dee82e2a8b6b007942303ffc. The generated
sandbox publisher, relock workflow, and restore bootstrap are based on v0.9.0 at
`603166a44c24bfba9d82d62f9f5638ca6ba31d9e`. Both pinned source revisions use the
same MIT notice (including the upstream OWNER copyright placeholder), preserved
verbatim in `licenses/pixi-sandbox-MIT.txt`; see `licenses/manifest.json`. No
automatic component version-bump/release policy was adopted.

Updating a managed copy is a deliberate dependency change: use the locked skills
CLI with a reviewed full commit URL, preserve its new lock output, refresh the
corresponding license/provenance notice, review the diff, then run `pixi run check`.
Do not hand-edit upstream copies or silently rewrite their hashes.

The explicit `.config/convco.yml` policy also adapts the pinned pixi-sandbox
`.versionrc` type/formatting conventions under the same preserved MIT notice.
Repository identity is ODM-conda, scope matching is anchored after testing Convco
0.7.2, and the single-project version/release policy was deliberately not copied.
