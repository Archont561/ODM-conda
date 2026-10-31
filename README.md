# Offline sandbox (orphan branch)

Built 2026-10-31T01:39:32Z from commit `b9979e8` for platform `linux-64`.
`pixi.lock` sha256 `f066746c2599d9cea26150790493df1595fc2841be992fef9fb91eb409a19ff5`.

The verified self-bootstrap binary is stored at `.pixi-sandbox/tools/linux-64/pixi-sandbox`. The branch root intentionally contains documentation only.

| env | platform | packed | unpacked | files |
| --- | --- | ---: | ---: | ---: |
| `agent-tools` | linux-64 | 47.0 MiB | 171.4 MiB | 35 |
| `default` | linux-64 | 87.5 MiB | 308.3 MiB | 55 |
| `odm-dev` | linux-64 | 709.4 MiB | 3125.2 MiB | 389 |


## Restore on the disconnected machine

```bash
./.pixi-sandbox/tools/linux-64/pixi-sandbox doctor --branch-location . --verify
./.pixi-sandbox/tools/linux-64/pixi-sandbox restore --branch-location . --output-path <project> --force
# then, from <project> with no network, use pixi as the sole entrypoint:
pixi install --frozen --offline
pixi run --frozen -- cargo build --offline
```

Every manifest blob is verified before it is written into the working tree.
