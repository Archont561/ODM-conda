---
id: doc-8
title: Archived native scaffold validation baseline
type: other
created_date: '2026-10-26 19:39'
updated_date: '2026-10-26 19:39'
---
# Archived native validation baseline

This is historical evidence, not a claim that the local binaries are still present.
The generated artifacts and standalone exports were removed by TASK-17.
Regenerate local artifacts with the maintained build/test/audit/source tasks when needed.

# Scaffold validation record

Date: **2026-10-26**. Environment: Linux x86-64 sandbox.

This records local checks, not a GitHub Actions run or an upstream endorsement.
No repository was created remotely and no package was uploaded to a public channel.

## Current tooling and Backlog validation

The tooling/Backlog/skills refresh evidence is maintained as Backlog **doc-5**,
not a parallel progress report. Read it with
`pixi run -e agent-tools bunx backlog doc view doc-5 --plain`.
The existing artifact snapshot below is the initial native build baseline;
those exact binaries were retested/re-audited, not rebuilt in the tooling refresh.

## Initial native scaffold baseline (before the tooling refresh)

| Check | Result |
|---|---|
| Manifest/recipe/source/notice/workflow structural lint | Passed |
| Offline packaging unit tests | **19 passed** |
| GitHub workflow validation with actionlint | Passed (1.7.12) |
| Both recipes rendered by rattler-build | Passed |
| `dem2points` native build | Passed |
| `fpcfilter` native build | Passed |
| Package-contained generated-data tests | Passed for both components |
| Fresh-environment artifact retests | Passed for both components |
| Identity, dependency, license-notice and ELF RPATH audits | Passed for both |
| Source-bundle construction and repeatability check | Passed for the two supported source graphs |
| Local release staging/checksum verification | Passed for FPCFilter; no upload performed |
| Release gate with scaffold defaults | **Correctly refused publication** |

The historical artifact audit snapshot is preserved verbatim as JSON below. The binaries named there
were produced locally for validation; they are not claimed to be published.

## Tools and native configuration

- Pixi: 0.82.0.
- rattler-build: 0.68.0.
- Repository Python: 3.12 (exact Conda build in `pixi.lock`).
- Compiler variant: GCC/G++ 14; the local solve selected 14.4.0.
- glibc sysroot variant: 2.28.
- CMake used by the starter build: 3.31.8.
- ELF audit tool: patchelf 0.19.2.
- Both installed native executables use `$ORIGIN/../lib` RPATH.

## Test coverage is intentionally limited

`dem2points` converts a generated flat 8x8 raster to 16 interior PLY points and
checks coordinates/elevation/normals. FPCFilter tests generated ASCII PLY
pass-through and actual radius decimation of normals-bearing binary PLY.

The initial no-normals sampling test exposed an upstream local-copy issue in the
pinned FPCFilter. That limitation is documented, not patched away or presented as
passing. Read Backlog TASK-2 (`pixi run -e agent-tools bunx backlog task TASK-2 --plain`) before approving a public release.

License/source-completeness review, all filtering modes, full ODM integration,
real drone datasets, older Linux runtimes, additional platforms and CUDA have not
been certified by these checks. OIDC authorization and the remote release flow
must still be configured and exercised by the repository owner.

All four human release acknowledgements remain **false** for both components in
this scaffold, despite the successful local starter tests.


## Original artifact audit snapshot

```json
{
  "date": "2026-10-26",
  "platform": "linux-64",
  "status": "local validation only; no upload",
  "artifacts": [
    {
      "component": "dem2points",
      "artifact": "dem2points-0.0.0.dev20220721-h873e7db_0.conda",
      "sha256": "c8160eb93d9362f5c0f25fe3b49f031edf50b1f807ab9d4e94e0100915787aad",
      "license": "GPL-3.0-only AND BSD-3-Clause AND MIT",
      "payload_files": 7,
      "metadata_license_files": 3,
      "runtime_dependencies": [
        "libgdal-core >=3.11,<3.12",
        "libgcc >=14",
        "libstdcxx >=14",
        "__glibc >=2.28,<3.0.a0",
        "libgdal-core >=3.11.5,<3.12.0a0"
      ],
      "rpath": "$ORIGIN/../lib",
      "source_commit": "4527122615f41044bde0e79850464ed33549ceeb",
      "result": "passed",
      "scope": "Artifact audit only; not a complete license or ODM integration review"
    },
    {
      "component": "fpcfilter",
      "artifact": "fpcfilter-0.2-h873e7db_0.conda",
      "sha256": "4fd7409b5cd46069c350800a94eac93300bf33f10d3a90aecdf8a862707e6b3e",
      "license": "GPL-3.0-only AND BSD-2-Clause AND MIT",
      "payload_files": 9,
      "metadata_license_files": 5,
      "runtime_dependencies": [
        "libgomp >=14",
        "libgcc >=14",
        "__glibc >=2.28,<3.0.a0",
        "libstdcxx >=14",
        "_openmp_mutex >=4.5"
      ],
      "rpath": "$ORIGIN/../lib",
      "source_commit": "6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b",
      "result": "passed",
      "scope": "Artifact audit only; not a complete license or ODM integration review"
    }
  ]
}
```
