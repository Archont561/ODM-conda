# Combined ODM environment inventory

[Private fresh linux-64 run 41085659812](https://github.com/Archont561/ODM-conda/actions/runs/41085659812)
built the three reduced candidates locally, installed them alongside six
previously validated component binaries into a new environment, and ran the
selected preflight and scoped-OpenSfM checks. It recorded 402 installed Conda
records in [`odm-combined-conda-inventory.json`](odm-combined-conda-inventory.json).
The run did not execute the Seneca pipeline. The complete sanitized metadata
was recovered from bounded job-log chunks by read-only
[run 41088000602](https://github.com/Archont561/ODM-conda/actions/runs/41088000602).
The `source_package_url` key from the original output was renamed to the more
accurate `binary_package_url`; the original serialized JSON SHA256 is recorded
in the file. No binaries, sources or imagery were uploaded.

The report contains all nine local package identities plus 393 Conda-forge
records. Conda records omit SHA256 for all nine local-file packages; the other
393 provide SHA256. The six reused package files were independently checked in
the inventory run (see its job annotations); hashes of the three newly built
packages are not established by this inventory. Thirteen `libopenvino` records
lack a license field. 305 records have no filename matching the notice-path
heuristic; this does not establish a missing notice or compliance. Binary
package URLs are not corresponding source URLs. This snapshot does not cover
pip distributions, package file bytes, exact upstream source, license obligations,
complete source offers, or runtime ABI and security validation. Package metadata
is an observation, not legal or release approval; repeated solves may differ.

### OpenVINO metadata investigation (2026-10-30)

The restored ODM development bundle contained all 13 binary archives named by
that inventory. Their independently calculated SHA256 values exactly matched the
inventory values. Examination of each `.conda` archive's `info/index.json`,
`info/about.json`, and `info/licenses/` found **no license field and no files
under `info/licenses/`** in any of the 13 archives. Each `info/about.json`
nevertheless lists four `license_file` paths, and identifies the same feedstock
revision, [`c362bec1c4eaf45e8f4b9e9f61847b97aba06045`](https://github.com/conda-forge/openvino-feedstock/tree/c362bec1c4eaf45e8f4b9e9f61847b97aba06045).
Per-package hashes and observed fields are in
[`openvino-binary-license-metadata.json`](openvino-binary-license-metadata.json).
These paths describe upstream source inputs, not files proven shipped in the
archive. Installed records also have no notice-like paths; neither filename
search establishes that no relevant text exists elsewhere in the payload.

The [feedstock recipe at that revision](https://github.com/conda-forge/openvino-feedstock/blob/c362bec1c4eaf45e8f4b9e9f61847b97aba06045/recipe/meta.yaml)
declares `Apache-2.0` in its top-level `about` section and the same license-file
paths for split outputs, but does not state an output-level license. It pins
OpenVINO 2025.4.1 primary source SHA256
`9926c8a8188d0baa9730623efaeb9f0bccf7059f5e4e957a8d238c3226c2b19b`
and multiple third-party source archives. The binary's embedded rendered recipe
is consistent with that source declaration; it has not been independently
reconstructed or proven complete. A [later upstream change](https://github.com/conda-forge/openvino-feedstock/commit/f50a776eaea6)
explicitly added output-level license fields for a newer 2026.0.0 build; it does
not retroactively change these 2025.4.1 binaries. The upstream declaration is
not proof that all bundled or linked material is Apache-2.0, nor that applicable
notices and source obligations are fulfilled. No dependency was silently upgraded
or license field fabricated; qualified review and any remediation remain open.

### Recheck with exact local binary hashes

[Private run 41090003564](https://github.com/Archont561/ODM-conda/actions/runs/41090003564)
built/retested/audited the three reduced research candidates, verified the six
previously retained binaries, and installed all nine into a fresh combined
linux-64 environment. It separately calculated SHA256 directly from the nine
local `.conda` files used by that run (not retroactively from the older
inventory). Read-only [run 41095611381](https://github.com/Archont561/ODM-conda/actions/runs/41095611381)
recovered the bounded identities from its log; no binaries or source archives
were uploaded.

| Local package | SHA256 |
| --- | --- |
| fpcfilter 0.2 b1 | `8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679` |
| dem2points dev20220721 b2 | `d7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f` |
| fastrasterfilter 1.0 b2 | `2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4` |
| odm-orthophoto dev20250225 b2 | `c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614` |
| renderdem 1.0 b1 | `451a291036f9bf11c140464d088884ec8980051c5383a667b75d1be7637fea77` |
| mvs-texturing-odm dev20250818 b2 | `af287aa4cb94f5b34e1e55d202e428123a1cc6d8ddc505ee74717e23ed92c4bc` |
| reduced PoissonRecon 13.8 b3 | `9a1cd8dbf03e5fa9a4d9d95e36a86726b8ff9802ed1d015f247420901d5e0eb4` |
| reduced-source scoped OpenSfM 0.5.2 b0 | `5886d1cda4aa20adddb614a212d15a4fdfb54dfb08277a6d14f3a894c078b08d` |
| reduced-tree OpenMVS dev20260516 b4 | `e56ce9a5a4e48453e564c35edd2b26150b396133c9290f5b5f8dd077d88d924e` |

The fresh solve again reported 402 Conda records, 13 missing license metadata
fields and nine local records without SHA256 metadata. This recheck recorded
counts and hashes, not a second complete retained transitive inventory; the
previous JSON is a different solve and must not be treated as its exact SBOM.
The installed-identity linkage and file hashes are not a byte-by-byte audit of
the installed prefix. Future inventories can optionally hash archive files via
`pixi run python scripts/inventory_conda_environment.py --prefix PREFIX --local-packages DIRECTORY`;
this helper is unit-tested, but was added after this native run, which calculated
its digests independently. All original release and rights caveats apply.
