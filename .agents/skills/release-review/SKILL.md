---
name: release-review
description: Review ODM component distribution, corresponding source and the isolated Prefix OIDC release workflow. Use before changing publishing gates, release tags, channel configuration or shipped artifacts.
---

# Review, do not auto-approve

The target is the EXISTING `archont561/archont561` channel. The GitHub repository
and its owner-controlled OIDC mapping may still need setup (TASK-15). Do not
assume access or create a new channel, token, repository or release implicitly.

1. Read the publishing guide (Backlog doc-7), licensing guide (doc-6), the component's Backlog tasks and
   all `release_checks` in `recipes/components.json`. Successful tests or a Done task do
   not supply legal/source review or publishing permission.
2. Verify source identity, actual supported targets, known limitations, notice
   inventory and complete corresponding-source coverage. Preserve required source
   availability and clear links. Actions artifacts expire and are not the source offer.
3. Verify the component version/build tag, clean trusted HEAD and immutable output.
   Packaging Conventional Commits do not automatically bump upstream versions.
4. Preserve source-before-binary ordering, OIDC/environment protection and narrow
   channel Read/write access. Never add long-lived all-channel credentials.
5. Preserve the isolated publishing job: no checkout and no execution of project
   scripts with upload credentials merely to make workflow YAML look uniform.
   The documented, minimal publisher shell exception is deliberate.
6. No automatic release per session, no gate flips without owner approval, no
   overwriting published artifacts and no silent skips of a filename collision.

Use default `pixi run release-check --tag ...` to demonstrate a blocked release;
never weaken the guard to make CI green. Keep unresolved owner actions and missing
native proofs open in Backlog. Any actual upload requires explicit authorization.
