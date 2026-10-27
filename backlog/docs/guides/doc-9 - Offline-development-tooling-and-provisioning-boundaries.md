---
id: doc-9
title: Offline development tooling and provisioning boundaries
type: other
created_date: '2026-10-26 20:37'
updated_date: '2026-10-26 20:43'
---
# Offline development: tooling is not the payload

## Existing dependencies

The default Pixi environment already declares locked conda-forge tooling: Python,
rattler-build, PyYAML, zstandard, patchelf, Convco, Lefthook, Taplo, Actionlint and
ShellCheck. The isolated agent-tools environment supplies Bun. Backlog.md and
skills are exact JavaScript development dependencies from package.json/bun.lock,
not Conda packages. Git, a shell and the Pixi executable remain host prerequisites.
The current host resolves Git and Bash from /usr/bin, not the Pixi prefix.

A lockfile records exact inputs; it does not contain executable packages. Neither
adding another dependency nor creating a sandbox config makes a cold machine offline-ready.

## Prepare while connected

```bash
pixi install --locked --all
pixi run -e agent-tools bun-install
pixi run check
```

This provisions both tool prefixes and the local Bun project dependencies on this
machine. Keep their installed files/caches available while disconnected. They
remain ignored local state, not source files to commit.

## Readiness on the same provisioned machine

```bash
pixi run --offline --locked check
```

Pixi's offline switch constrains Pixi's own access; it is not a network firewall
for Bun, Git, source downloads or child processes. Frozen Bun installation pins
versions but is not an offline switch. Its installed dependencies/cache must be
provisioned separately. Updating managed skills or fetching new dependencies still
needs cached inputs or a connection. A warm-prefix success is not a clean-machine
restore proof, and a normal recipe render does not compile native software.

## Native recipe builds need more

Build/host/test/runtime packages (compiler, sysroot, CMake, Ninja, GDAL and other
selected libraries) belong to rattler-build's isolated environments, not the outer
Pixi tooling prefix. Offline native builds additionally need the required package
archives/metadata or local channels, exact upstream sources/patches and test inputs.
Source bundles do not contain Conda dependency binaries. The prior cleanup removed
project-local build/source/staging caches; no complete cold-cache native offline
build or full ODM/NodeODM offline environment has been certified.

## Another or clean machine

Use a platform-matched, validated relocatable environment transport or local
package caches/channels, including both default and agent-tools prefixes plus Bun
project dependencies/cache and the Pixi/Git/shell bootstrap. Do not assume copying
.pixi verbatim will relocate correctly. A pixi-sandbox plan would be a separate,
explicit feature: this Python/C++ packaging repo has no Cargo workspace to vendor,
and a plan covering only default would omit Bun. Any distributed binary transport
also needs its own applicable notices/source review.

Convco adoption does not create a transport, add a publisher, grant upload rights,
or certify native dependencies. The existing archont561/archont561 channel and all
human release gates remain unchanged.

## Observed warm-machine validation — 2026-10-26

On the existing Linux x86-64 host, the locked/offline common gate (44 Python and
four Bun tests, metadata, skill hashes, Actionlint/ShellCheck and both recipe
renders) and a real Backlog task-list read passed while child processes were
restricted with Linux seccomp: new non-AF_UNIX sockets and io_uring interfaces
were denied. A separate probe confirmed IPv4/IPv6 socket creation failed while
local IPC worked. This used the installed default/agent-tools prefixes, existing
node_modules/cache and host Git/shell, with telemetry disabled in the test.

That observation does not certify a cold-cache install, machine relocation,
additional platforms, skill updates, native compilation or full ODM execution.
No portable transport was built and no sandbox publisher was added.

## Local pixi-sandbox pack and restore — 2026-10-27

Performed on this host only. Nothing was published and no sandbox branch was pushed.

- Lock check: `pixi install --locked --all` succeeded for default and agent-tools, so `pixi.lock` matches `pixi.toml` (linux-64 only, the only platform the project declares).
- Tool: pixi-sandbox 0.9.0 standalone, checked against the release `SHA256SUMS` before use. `plan --config pixi-sandbox.toml --json` emitted one linux-64 developer bundle for `default,agent-tools` on `sandbox/developer-linux-64`.
- Pack: `pixi-sandbox pack --envs default,agent-tools --platform linux-64 --pixi-bin <pixi> --self-bin <pixi-sandbox>` produced 80 blobs, 205.8 MiB, recorded at commit `8ee417b`. The first pack omitted `--self-bin`; `restore.sh` expects that binary under `.pixi-sandbox/tools/linux-64/`, so it is required.
- Verify: `doctor --verify` passed (0 failures). Restore into a scratch copy of the committed tree passed `--verify-restored` for both environments. `pixi install --frozen --offline` was a no-op there, and `python`, `bun` and `rattler-build` ran offline.
- Not covered: Bun `node_modules` is not packed (pixi-sandbox has no mechanism for it); native build environments for the recipes are rattler-build's; other platforms are not declared by the project.
