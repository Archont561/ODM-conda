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

### Newer OpenVINO compatibility and notice probe (2026-10-30)

[Private combined run 41097529820](https://github.com/Archont561/ODM-conda/actions/runs/41097529820)
built and retested the three research candidates and attempted to install them
alongside the six retained packages with `libopenvino >=2026.0`. The **combined
solve failed**: the newly built OpenMVS package requires
`libopencv >=4.12.0,<4.12.1.0a0`; the available 4.12.0 solver candidates in
that run required OpenVINO versions 2025.0.0, 2025.2.0, 2025.3.0 or 2025.4.1,
not 2026. A separate [minimal solver run 41097698612](https://github.com/Archont561/ODM-conda/actions/runs/41097698612)
confirmed the same conflict for Python 3.12 and OpenCV 4.12 constraints; its
error was recovered by [41097771349](https://github.com/Archont561/ODM-conda/actions/runs/41097771349).
The other job in the combined run failed before solving due to an invalid
`pixi init --scm none` option; it is not evidence about compatibility. Because
the actual nine-package solve failed, **no newer-OpenVINO combined preflight,
Seneca pipeline, or raster validation ran** in this experiment. No requirements
or existing audits were weakened.

An independent [probe 41097920931](https://github.com/Archont561/ODM-conda/actions/runs/41097920931)
with Python 3.12, OpenCV `>=4.13,<5` and OpenVINO `>=2026` did solve and install
OpenCV 4.13.0 build `qt6_h7897e75_619`, py-opencv 4.13.0 build
`qt6_h06c354c_619` and OpenVINO 2026.4.1 build `hbb11d60_0` (identity
recovered by [41098068203](https://github.com/Archont561/ODM-conda/actions/runs/41098068203)).
This was **not** a nine-package solve or an ABI/functional test; the existing
OpenMVS package's `<4.12.1.0a0` dependency rules it out. A candidate upgrade
would require deliberate rebuilds and native retests against a new OpenCV ABI,
or an independently reviewed OpenCV 4.12 variant without the old dependency.
Neither route is validated here.

Archive inspection findings, each downloaded binary checked against its solved
SHA256, are recorded as follows:

- [2026.0.0 build 1 standalone](openvino-2026-binary-metadata.json),
  [run 41097867840](https://github.com/Archont561/ODM-conda/actions/runs/41097867840):
  all 13 requested split packages have `Apache-2.0` index/about license fields,
  but none contains files under `info/licenses/`. The later field fix alone
  therefore did not address this notice-location gap.
- [2026.4.1 build 1 standalone](openvino-2026-4-binary-metadata.json),
  [run 41098131974](https://github.com/Archont561/ODM-conda/actions/runs/41098131974):
  13 requested split packages each have `Apache-2.0` metadata and four files
  under `info/licenses/`.
- [OpenCV 4.13 alternative solve](openvino-opencv-413-probe-metadata.json),
  [run 41098426733](https://github.com/Archont561/ODM-conda/actions/runs/41098426733):
  a separate repeat solve selected **14** OpenVINO 2026.4.1 build-0 packages
  including a GGUF frontend; each has `Apache-2.0` metadata and four
  `info/licenses/` files. These are not the build-1 archives above.

The selected build-0 binaries identify [feedstock commit c82659b5f2f7ba9b519179764c700478326726ac](https://github.com/conda-forge/openvino-feedstock/tree/c82659b5f2f7ba9b519179764c700478326726ac).
Its [recipe](https://github.com/conda-forge/openvino-feedstock/blob/c82659b5f2f7ba9b519179764c700478326726ac/recipe/meta.yaml)
pins the main OpenVINO 2026.4.1 archive SHA256
`1ee85264556025486a4745a2d452ea823c578b3d162768bfef590366d2e6c539`,
plus multiple third-party archives and patches. The main archive was independently
fetched and its SHA256 matched; the four corresponding files in that archive
matched the notice SHA256 values in all 14 inspected build-0 binaries. The other
archives, compiler/toolchain inputs and transitive sources were not independently
verified. A matching notice file or a declared license is not proof of source,
notice, or license-obligation completeness and does not authorize release.

### OpenCV 4.13 private variant preparation

The previous nine-package set contains three recipes with direct OpenCV 4.12
requirements: `odm-orthophoto`, scoped OpenSfM and reduced OpenMVS. The other
six have no direct OpenCV requirement in their recipes; this does not prove
that their transitive dependencies or ABI are compatible. In particular,
OpenMVS's previously solved binary had an exact 4.12 runtime constraint.

`pixi run python scripts/prepare_opencv413_research.py --destination /path/outside/repo`
creates a disposable copy of the packaging inputs and changes only those three
recipes' host/run OpenCV constraints to `>=4.13,<4.14`. The three copied
recipes are explicitly marked as private ABI experiments; production recipes,
source fingerprints and audit scripts are unchanged. The copy is **not** a
build, audit, source offer or release candidate. Names and build numbers are
unchanged in these temporary recipes, so the resulting binaries must not be
published or confused with the approved production artifacts. Rebuild, fresh
test, audit and integration evidence are required for any future variant.

[Private run 41102357808](https://github.com/Archont561/ODM-conda/actions/runs/41102357808)
built analogous temporary OpenCV 4.13 recipe copies and passed native builds,
installed and fresh tests, and their existing respective package audits for
orthophoto, reduced-source scoped OpenSfM, and reduced-tree OpenMVS. Reduced
PoissonRecon was also built, fresh-tested and audited; five previously retained
components were independently hash-verified. All nine packages solved together
with `libopenvino >=2026.0`, and the selected preflight and scoped mode guards
passed. The completed Seneca run and live GDAL metadata/statistics sanity check
produced a 9508 × 10599 RGBA Byte raster, EPSG:32617, geotransform
`[305967.61184717366, 0.0499971454197316, 0, 4545655.251033577, 0, -0.0499993027651392]`.
The raster and report were discarded; no research binaries, source archives or
imagery were uploaded. No visual/geographic accuracy or dataset-rights review
is implied.

The run recorded 424 Conda records, zero records missing a license metadata
field and nine local records missing SHA256 metadata. These are counts, not a
retained transitive inventory or legal clearance. The exact resolved OpenVINO
version and complete dependency set were not recorded by this trial; only its
`>=2026.0` constraint and the successful solve are established. The temporary
local package hashes emitted by that run were:

- orthophoto `5453e33dcdbe12d55ba8c8303c0189aead297dbe0397c6183798232bdfb003ab`
- scoped OpenSfM `5c2c0093bdc500d64b2a3056a74b73912297e005de6e1a696952b665b3cc0e7c`
- reduced OpenMVS `a7375b1874f763a60bfdb3e902bfa6bcbe411e1de479dabe05db3fa3772a15d5`
- reduced PoissonRecon `46469cfedb22d7522496283b4333a8eb917c8a774b8465f3ac4e6e074ee7a493`

The run used a temporary script implementing the same three staged recipe
edits; it did **not** invoke the subsequently added preparer. The temporary
script and workflow were removed from the final tree. Its experiment retains
normal package names and build numbers: passing existing audits does not
establish that its modified orthophoto recipe corresponds to any published
production source or authorize distribution. The earlier report that the runner
had not started was incorrect: GitHub's job details were temporarily incomplete.
Local conda-forge solving failed TLS in this sandbox; the hosted run succeeded.
All existing source, notice, release and dataset-rights gates remain open.

### Fresh OpenCV 4.13 dependency trial

[Private run 41109317029](https://github.com/Archont561/ODM-conda/actions/runs/41109317029)
rebuilt the private variants, fresh-tested and audited them, installed the nine
components, checked `pixi install --locked`, and completed the Seneca pipeline
and raster sanity checks. Its sanitized dependency snapshot is
[`odm-opencv413-dependency-trial.json`](odm-opencv413-dependency-trial.json),
recovered by [read-only run 41112705697](https://github.com/Archont561/ODM-conda/actions/runs/41112705697).
No package, source or imagery was uploaded. This is a **new solve**, not proof
of the exact version selected by the prior trial 41102357808.

The new linux-64 environment contained 424 installed Conda records, including
nine local research/reused packages, and 16 PyPI lock records. All 16 PyPI
records have SHA256 values in the captured lock metadata. The nine local Conda
records lack SHA256 metadata, but the nine input archives were separately
hashed and are listed in the snapshot. No Conda record lacked a license
metadata field; that does not constitute a license, notice or completeness audit.
Selected Conda records include:

| Package | Version | Build | Binary SHA256 |
| --- | --- | --- | --- |
| libopenvino | 2026.2.1 | `h1f0fae8_1` | `7941fb9ba8c3a5a0a2401dc4120e8fcb561b96d928c43374eb93f545019a2858` |
| libopencv | 4.13.0 | `qt6_hf3622b9_613` | `b8d19c56050c928b49372c2e173ec8aa547c2914c90890d02680e5e9ebf23042` |
| py-opencv | 4.13.0 | `qt6_h6945e2d_613` | `7e151685d5554c039b2de5564681d8de03afbf08444b713607556787a8fb161a` |
| libgdal-core | 3.12.2 | `he63569f_2` | `564d9e27f9cb3eae53a945a70c25b92f22f74a27b450dc166a255964623b4383` |
| libpdal-core | 2.10.0 | `h9d23c72_0` | `c43a137e3b537f8842b3c850e9a319b9cae0ab59143b4fc7358495892e61d279` |

The snapshot is an **inventory, not a runnable Pixi lock**: local absolute
paths and original binaries were not retained, and the original lock is not
included. The original locked environment was checked in place, but a separate
fresh-prefix replay of that exact lock was not performed. Its recorded SHA256
identifies the original lock bytes for comparison, including private path
references; it cannot reconstruct those bytes. Thus exact future replay and
byte-identical local rebuilds are not established. The report captures installed
Conda metadata and PyPI lock records, not wheel payload audits, corresponding
sources or legal obligations. `scripts/inventory_pypi_lock.py` provides a
separate tested utility to summarize selected PyPI lock records while stripping
credentials and local paths; the hosted trial used an equivalent temporary
capture rather than that subsequently added utility. Existing software and
dataset-rights gates remain open.

### Private, relocatable lock replay (2026-10-30)

[Private run 41115458840](https://github.com/Archont561/ODM-conda/actions/runs/41115458840)
built and fresh-tested/audited the private 4.13 orthophoto, scoped OpenSfM and
OpenMVS variants and reduced Poisson. It indexed their nine exact input archives
in a local channel, solved a new environment, and generated a Pixi lock normally
(no manual lock edits). The local channel was served **only on loopback** at a
fixed port. The lock, manifest and channel were copied to a different directory;
the original channel was removed, each relocated archive hash checked, the
server restarted at the same loopback URL, and `pixi install --locked` was run
into a fresh prefix with a separate home and caches. The lock remained
byte-identical (SHA256
`fb28601ad4ef3ee2c4327a825ba098e49b0ed1f34b109ecd9a2405d009516681`),
and all 424 Conda package identities, builds, metadata hashes and sanitized
URLs matched between prefixes. The selected PyPI dependencies came from the
same copied lock; this was not an independent byte-by-byte audit of installed
PyPI distributions. The relocated prefix passed preflight, scoped guards, the
Seneca pipeline and live raster sanity checks. Outputs were discarded.

A bounded sanitized snapshot is
[`odm-private-lock-replay-inventory.json`](odm-private-lock-replay-inventory.json),
recovered by [41118954520](https://github.com/Archont561/ODM-conda/actions/runs/41118954520).
It records 424 Conda records, 16 PyPI lock records and nine local archive
hashes; all 424 Conda records in this trial carry SHA256 metadata. The inventory
sanitizer intentionally strips URL ports, so its `127.0.0.1` entries are
identifiers, **not usable package URLs**. Selected OpenVINO was 2026.2.1
`h1f0fae8_1`, but this does not identify other solves. A present license field
or matching hash does not prove legal compliance or complete corresponding
source.

For a future **private** replay, make an isolated directory outside the repo,
use `pixi run python scripts/private_conda_channel.py --destination CHANNEL
PACKAGE...` on the exact nine audited archives, and bind a temporary server to
`127.0.0.1` only (for example `python -m http.server 48179 --bind 127.0.0.1
--directory CHANNEL`). Create a Pixi workspace with that loopback channel
before conda-forge, add the nine package **names** plus the required runtime
and PyPI dependencies, and let Pixi create the lock. Keep the lock, manifest,
channel and checksums together in access-controlled private storage. To replay,
move the bundle, verify package hashes, serve the same loopback URL/port, and
run `pixi install --locked` in a new prefix. Never edit `pixi.lock` by hand or
publish the private channel, binaries or source archives. The helper only
indexes explicit archives; it does not audit or authorize them.

This experiment used a fixed linux-64 platform and available conda-forge/PyPI
packages, not an offline or cross-platform replay. The original lock and
binaries were deliberately discarded after the test; the snapshot is not a
runnable lock and cannot recreate them. Byte-identical rebuilds, complete
sources and notices, dataset rights, visual/geographic accuracy and release
approval remain unestablished. The private research variants reuse normal
package names/build numbers and must not be confused with production artifacts.

### Exact replay OpenVINO source and notice inspection (2026-10-30)

[Private inspection 41121075671](https://github.com/Archont561/ODM-conda/actions/runs/41121075671)
downloaded the **13 exact 2026.2.1 linux-64 OpenVINO archives** selected by the
replay, independently checked each archive SHA256 against the captured
inventory, and inspected its Conda metadata. All 13 index/about license fields
say Apache-2.0; their embedded rendered recipes name feedstock commit
[`60076581dd7818d779760e0937f869dfe992eb7b`](https://github.com/conda-forge/openvino-feedstock/tree/60076581dd7818d779760e0937f869dfe992eb7b)
and the same seven applicable source URLs and hashes. Each has the same four
`info/licenses` files. All four hashes match the respective files in the
verified OpenVINO 2026.2.1 primary source archive. The exact archive and recipe
hashes, pins and notice hashes are recorded in
[`openvino-2026-2-replay-metadata.json`](openvino-2026-2-replay-metadata.json).

All seven source archives listed by the **rendered linux-64 recipe** were
fetched separately and their SHA256s matched their pins: OpenVINO, CPU oneDNN,
KleidiAI, MLAS, GPU oneDNN, level-zero NPU extensions, and ONNX. The ARM
ComputeLibrary source is conditional and absent from this linux-64 rendered
recipe; it was not verified. These checks do not verify patch contents, build
reproducibility, every transitive dependency or submodule, source sufficiency,
license applicability or the completeness of notices. The archives were not
retained or redistributed. Owner/qualified review and release gates remain open.
