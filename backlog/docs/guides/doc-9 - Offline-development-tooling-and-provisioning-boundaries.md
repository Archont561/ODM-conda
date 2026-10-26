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
