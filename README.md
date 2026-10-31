# ODM Conda packages

[![CI](https://github.com/Archont561/ODM-conda/actions/workflows/ci.yml/badge.svg)](https://github.com/Archont561/ODM-conda/actions/workflows/ci.yml)

Unofficial, modular [OpenDroneMap](https://github.com/OpenDroneMap/ODM) components for Conda, built with Pixi and rattler-build.

**Status:** Linux x86-64 CPU components, based on ODM 3.6.2. This is not yet a complete ODM or NodeODM distribution.

## Packages

Available from the [archont561/archont561 channel](https://prefix.dev/channels/@archont561/archont561):

| Component | Version | Build |
| :-- | :-- | --: |
| `dem2points` | `0.0.0.dev20220721` | 2 |
| `fastrasterfilter` | `1.0` | 2 |
| `fpcfilter` | `0.2` | 1 |
| `odm-orthophoto` | `0.0.0.dev20250225` | 2 |

`dem2mesh`, `renderdem`, `poissonrecon-odm` and `mvs-texturing-odm` have recipes but are not approved for publication. OpenSfM and OpenMVS are [local-only research](research/README.md), not for redistribution. See [component release gates](recipes/components.json) for the authoritative status.

## Try it

On Linux x86-64 with [Pixi](https://pixi.sh/):

```sh
pixi init --channel https://prefix.dev/archont561/archont561 --channel conda-forge odm-tools
cd odm-tools
pixi add fastrasterfilter
```

Add other published components with `pixi add <component>`. [GitHub releases](https://github.com/Archont561/ODM-conda/releases) provide binaries, corresponding source and checksums.

## Validation

The four published components have passed installed functional tests together in a fresh Linux prefix. A disposable fast-orthophoto trial using those packages and five local-only components completed on the Seneca dataset; its final raster metadata and statistics were checked. Neither result establishes visual or geospatial accuracy, full-prefix relocation, or redistribution rights for research components. See the [integration evidence](research/odm-fast-orthophoto-prototype.md) for details.

Only Linux x86-64 CPU is targeted. The glibc 2.28 sysroot is a toolchain baseline, not a tested runtime guarantee.

## Develop

```sh
./restore.sh                       # restore locked developer environments
pixi run check                     # static checks, tests and recipe renders
pixi run build --component fpcfilter
pixi run test --component fpcfilter
pixi run audit --component fpcfilter
pixi run sources --component fpcfilter
```

Native builds need source and Conda dependency access. `pixi run check` does not compile components. The owner-dispatched **Build and test native components** workflow supports selecting multiple recipes. Its ODM checkbox runs a separate private research build and replay without uploading its outputs; it does not publish them.

## Documentation

- [Contributing](.github/CONTRIBUTING.md)
- [Licensing and source checklist](backlog/docs/guides/doc-6%20-%20Licensing-and-source-distribution-checklist.md)
- [Publishing guide](backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md)
- [Component readiness](research/component-readiness-review.md)
- [ODM integration prototype](research/odm-fast-orthophoto-prototype.md)
- [Offline development](backlog/docs/guides/doc-9%20-%20Offline-development-tooling-and-provisioning-boundaries.md)
- [Backlog](backlog/) and [agent instructions](AGENTS.md)

## License

The root [MIT license](LICENSE) covers original packaging code only. Upstream components and bundled code retain their own licenses and notices; passing tests are not release approval or a complete legal review.
