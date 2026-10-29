# ODM Conda packages

[![CI](https://github.com/Archont561/ODM-conda/actions/workflows/ci.yml/badge.svg)](https://github.com/Archont561/ODM-conda/actions/workflows/ci.yml)

**Unofficial, modular [OpenDroneMap](https://github.com/OpenDroneMap/ODM) components for Conda.**

Recipes use Pixi and rattler-build and target Linux x86-64 CPU. The reference is
ODM 3.6.2; this repository is **not** a complete ODM or NodeODM distribution.

## Packages

Published to the existing [`archont561/archont561` channel](https://prefix.dev/archont561/archont561):

| Component | Published version | Build |
| :-- | :-- | --: |
| `fastrasterfilter` | `1.0` | 2 |
| `fpcfilter` | `0.2` | 1 |
| `dem2points` | `0.0.0.dev20220721` | 2 |
| `odm-orthophoto` | `0.0.0.dev20250225` | 2 |

The other registered recipes are `dem2mesh`,
`renderdem`, `poissonrecon-odm` and `mvs-texturing-odm`; they are not approved
for publication. [Component identities and release gates](recipes/components.json)
are authoritative. Research-only OpenSfM and OpenMVS recipes are not for
redistribution; see [research](research/README.md).

## Install

On Linux x86-64 with [Pixi](https://pixi.sh/), create a project and add a
published component. Conda-forge supplies its dependencies.

```sh
pixi init odm-tools
cd odm-tools
pixi workspace channel add https://prefix.dev/archont561/archont561
pixi workspace channel add conda-forge
pixi add fastrasterfilter
```

See [releases](https://github.com/Archont561/ODM-conda/releases) for package
assets, corresponding source and checksums. Packages are separate native tools;
there is no supported `odm` application command yet.

## Develop

```sh
./restore.sh                       # restore locked developer environments
pixi run check                     # static checks, tests and recipe renders
pixi run build --component fpcfilter
pixi run test --component fpcfilter
pixi run audit --component fpcfilter
pixi run sources --component fpcfilter
```

Native builds need source and Conda dependency access. `check` does not compile
components; native builds also run installed tests, with a separate fresh retest
and audit. The owner-dispatched **Build and test native components** workflow
can select multiple recipes with checkboxes; it does not publish them. Only
Linux x86-64 CPU is currently targeted; the glibc 2.28 sysroot is a toolchain
baseline, not a tested runtime guarantee.

## Documentation

- [Contributing](.github/CONTRIBUTING.md) — setup, checks and change policy
- [Licensing and source checklist](backlog/docs/guides/doc-6%20-%20Licensing-and-source-distribution-checklist.md)
- [Publishing guide](backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md) — review gates and source-before-binary releases
- [Component readiness and limitations](research/component-readiness-review.md)
- [ODM integration prototype](research/odm-fast-orthophoto-prototype.md)
- [Offline development](backlog/docs/guides/doc-9%20-%20Offline-development-tooling-and-provisioning-boundaries.md)
- [Backlog](backlog/) — tasks, decisions and progress; contributors using agents start with [AGENTS.md](AGENTS.md)

## License

The root [MIT license](LICENSE) covers original packaging code only. Upstream
components and bundled code retain their own licenses and notices; successful
tests are not release approval or a complete legal review.
