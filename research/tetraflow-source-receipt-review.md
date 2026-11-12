# TetraFlow research inputs: bounded source review and private receipt

This is **not a legal opinion, independent provenance determination,
corresponding-source offer, release bundle, or publication approval**. It
covers only the two primary source archives and repository packaging inputs
for the private TetraFlow ReconstructMesh experiment, not the ODM stack.

## What was inspected

The archive hashes match the private recipe. A local archive inventory found
485 regular OpenMVS files (9,223,257 bytes) and 1,784 Eigen files (15,465,286
bytes). Neither archive had symlinks. There are no files under the named
`libs/Math/IBFS` or `libs/Math/TRWS` paths in this OpenMVS archive. This is a
path observation, **not** proof no restricted code appears elsewhere.

| Item | Bounded evidence | Remaining question |
| --- | --- | --- |
| `LICENSE` | AGPL text; SHA256 `0f072d4a0ef59e7f6864bb45629c37417ccef63025b58f4073109d1c830bc55f`. `SceneReconstruct.cpp` and `ReconstructMesh.cpp` contain AGPL notices. | Review exact file grants, contributors, combined work and source/notice obligations. |
| `libs/Math/TetraFlow.h` | SHA256 `dd3376a592b4c52321b8ab2130cfaadb0ed3b03980a0c7608ad9c98f73c2b380`, copyright 2026 cDc, declares Boost 1.0; claims independently written from the published algorithm. | Neither the notice nor a commit identity independently establishes originality or chain of title. Qualified provenance review is still needed. |
| `libs/IO/PLY.cpp` | Header declares Boost 1.0, copyright 2023 cDc. | Review actual file history, modifications and notice obligations. |
| `libs/Math/LMFit/COPYING` | Contains FreeBSD license and named copyright holders; SHA256 `09c21b5a8ca469b20e0ce3795f19370affba36f532e480e593c9712c91caf4c4`. Build includes LMFit sources. | Determine applicable notices and confirm the exact compiled inputs. |
| `COPYRIGHT.md` | Upstream names several third-party projects; SHA256 `c231e8064c5afb62b99c49969cd0f0b8d5082f754e9950f4ff8dd20ebe7d1062`. | It is an upstream summary, not a complete or verified bill of materials. |
| Eigen | `COPYING.README` says primarily MPL2 with some BSD/LGPL files; `COPYING.MPL2` SHA256 `fab3dd6bdab226f1c08630b1dd917e11fcb4ec5e1e020e2c16f83a0a13863e85`. The recipe defines `EIGEN_MPL2_ONLY`. | The archive contains additional license files. A compile flag is not a provenance, complete-source or notice determination. |

A filename heuristic found four OpenMVS notice-like paths, including the
SiftGPU port's separate `LICENSE`, and ten Eigen paths (including a script
whose name contains `relicense`). Some are outside the selected build;
others may have notices embedded under different names. This is **not** a
complete notice list or evidence that any item may be omitted. The original
archives contain files beyond the reduced ReconstructMesh build; retaining or
redistributing an entire archive requires its own rights analysis.

## Private input receipt

`scripts/tetraflow_source_receipt.py` accepts the caller-supplied, exact
OpenMVS and Eigen archives, verifies their pinned digests, checks tar member
paths/types/limits, inventories each file's hash and size, and records
notice-like filenames. It also refuses the two named restricted OpenMVS paths.
It copies the archives and selected recipe, patch, build and test scripts to a
new directory **outside** the checkout, writing a hash-addressed `receipt.json`.
Use only trusted owner-controlled private storage, after the owner determines
that holding these materials there is appropriate. Do not upload this receipt
or its archives as a GitHub artifact or publish them.

```sh
python scripts/tetraflow_source_receipt.py stage \
  --openmvs /private/openmvs.tar.gz --eigen /private/eigen.tar.gz \
  --destination /private/new-tetraflow-input-receipt
# Record the printed manifest SHA256 separately, outside the receipt.
python /private/new-tetraflow-input-receipt/packaging/scripts/tetraflow_source_receipt.py verify \
  --receipt /private/new-tetraflow-input-receipt --manifest-sha256 <independently-recorded-sha256>
```

Verification checks the independently supplied manifest hash, exact file set,
file hashes, and re-inventories both pinned source archives. It does not
authenticate the external manifest hash or establish the identity of whoever
created it. It does not rebuild, verify installed bytes, inspect all license
headers, determine rights, or prove corresponding-source completeness. The
receipt omits binary packages, the Conda host/build/runtime closure and their
sources, compilers, patches and build tools beyond the selected repository
inputs, final lock/inventory, and full ODM/OpenSfM/JPEG XL materials. No
production recipe or owner release gate is created by this work.

A local private experiment made and relocated a receipt from the two verified
archives, then verified the relocated copy with its separately passed manifest
hash `60d1f345cc5348d11f533413ed9aafe8e238dd951962b754052560501b27df1e`.
It contained 17 receipt files plus the manifest; the archives and receipt were
not uploaded or retained as a release artifact. Tests cover mutation, extra
files, symlinks, traversal, duplicate members, restricted paths, private
destination and relocated verifier bytecode behavior.

## Still required

- Qualified independent review of the exact archive, provenance, all selected
  source, third parties, notices, and legal ability to store and distribute it.
- Capture and review the exact compiler, build/host/runtime dependencies,
  source archives, patches, scripts, notices and generated files for the final
  build, including external codec and CGAL/Boost/Eigen obligations.
- Create, retain and independently replay the exact owner-controlled ODM
  bundle and final lock; review OpenSfM, JPEG XL and other unresolved sources.
- Only after decisions and validation, prepare/register production recipes and
  obtain the owner's distinct gates and publication authorization.

## Private ODM bundle option (not a release)

The private bundle builder accepts `--openmvs-variant tetraflow`, selecting the
new research-only package and a distinct ODM build string. It retains the
existing audits for other components and performs an additional **bounded**
TetraFlow package identity, exact payload/fixture, five selected metadata
notice hashes and ELF RPATH check. The build also retains its source-file and
named-link-map guards. These checks do not prove provenance, rights, complete
notices, complete sources or all linked inputs. They do not replace a release
audit. A relocated replay with the TetraFlow package checks runtime linkage.
The previous `historical` default remains unchanged and still fetches the
historical source archive with restricted material; it is not cleared.

For a suitably access-controlled, private owner host with locked Pixi tools,
network access to Conda and pinned sources, and the verified original
`jpegxl-src` crate already available:

```sh
pixi run python scripts/private_odm_bundle.py build \
  --destination /private/new-odm-bundle --openmvs-variant tetraflow \
  --runtime-profile reduced --vendor-scope-crate /private/jpegxl-src-0.11.2.crate \
  --dataset /private/suitable-local-dataset
# Independently record the printed private-bundle.json SHA256, then:
pixi run python scripts/private_odm_bundle.py replay \
  --bundle /private/new-odm-bundle --manifest-sha256 <independently-recorded-sha256> \
  --dataset /private/suitable-local-dataset --test-jxl
```

The dataset argument is optional; without it there is no end-to-end dataset
validation. The owner must establish appropriate authority to use any dataset.
The destination must be new, outside the checkout, and kept private. The bundle
contains local research binaries and its lock and Conda installation inventory;
external Conda packages may be fetched during replay, and source archives,
compiler/build/host closure, full source obligations and legal permissions are
not captured. Do not describe it as a final or offline release bundle. Record
the manifest digest through a separate trusted channel. No owner storage was
provided for this task, so no owner-retained bundle was produced here.

The first new builder trial [43116155321](https://github.com/Archont561/ODM-conda/actions/runs/43116155321)
built and tested the alternate but the new audit rejected its additional,
compatible libjxl run-export constraint. After accounting for multiple
constraints, [43119210985](https://github.com/Archont561/ODM-conda/actions/runs/43119210985)
exposed a transcription error in the pinned Eigen MPL2 hash. The hash was
corrected to the archive's value; the independent package build, retest and
bounded audit passed in [43119773206](https://github.com/Archont561/ODM-conda/actions/runs/43119773206).

The complete repeat using the new builder
[43120174240](https://github.com/Archont561/ODM-conda/actions/runs/43120174240)
passed the package builds and selected research audits, relocated locked replay,
linkage and JPEG XL checks, Seneca fast-orthophoto processing and raster sanity.
The full run used the audit before its subsequent stricter exact constraint parser;
the parser change has local negative and positive unit tests. These hosted trials
discarded binaries, sources, locks and dataset outputs rather than uploading them.
This success is not an owner-retained bundle or a legal, security, quality,
source-completeness or release approval.

## Build input metadata (one trial only)

The metadata-only inventory `tetraflow-build-input-inventory.json` records the
47 build and 207 host records embedded by rattler-build in the output of
[43200317453](https://github.com/Archont561/ODM-conda/actions/runs/43200317453).
Its SHA256 is `0e0add60bc04181a165c763fe466b9c1db754cfa0302bdb3af99d36258d7bd6d`;
the discarded output package SHA256 is
`1d8344e35dcb362db9012961df8782a319791a5ca08b9122755b63d7022c3217`.
The extractor can be run on a retained package with
`pixi run python scripts/conda_build_provenance.py --package /private/package.conda`.
It reports recorded binary identities, hashes, public URLs and declared license
metadata, not independently verified installed bytes, source archives, actual
linkage, a reproducible build, complete obligations or legal approval. It is
not the dependency closure of earlier runs or of the complete ODM bundle.
The trial selected GCC/G++ 14.4.0, CGAL 6.2.1, Boost 1.90.0, OpenCV 4.13.0,
libjxl 0.11.2, nanoflann 2.0.1 and TBB-devel 2023.1.0; TBB-devel's recorded
license is absent. All declared licenses require independent review.

A separate metadata probe
[43201060262](https://github.com/Archont561/ODM-conda/actions/runs/43201060262)
downloaded and SHA256-checked the specific recorded CGAL, libboost-devel and
nanoflann binaries, and inspected their embedded recipes. They declare,
respectively: CGAL 6.2.1 source SHA256
`b6be77c60765a8456335de991eeaf6ffec55256984e4a9ecc6a97c37bbfe85bf`,
Boost 1.90.0 source SHA256
`49551aff3b22cbc5c5a9ed3dbc92f0e23ea50a0f7325b0d198b705e8ee3fc305`
with a recipe patch, and nanoflann 2.0.1 source SHA256
`bb3991ad924248d3f20953a951c34878196c11ca112d800acc341c3808443896`.
Those probe results are recipe declarations, not source downloads or independent
source verification. The remaining binaries, recipes, patches, toolchain, transitive
sources and any corresponding-source or notice obligations remain uncollected
and unreviewed. A prior probe encountered a link in a libjpeg-turbo package and
correctly stopped rather than relaxing the starter-package archive guard.
No source archives, binary packages or datasets were published by these probes.

## Independent nanoflann archive check

For the trial's host `nanoflann 2.0.1` package, the source declaration above
matches the SHA256 of the separately downloaded
[upstream tag archive](https://codeload.github.com/jlblancoc/nanoflann/tar.gz/refs/tags/2.0.1).
The archive was inventoried without extraction: 131 regular files, 2,293,071
bytes, no links or special entries accepted. The filename heuristic identified
`COPYING` (SHA256 `12e2e0baacf7fa6291e6058a7cd0e680d9b7c1e29df791ac2695e3cb9517b9d7`)
and `.circleci/clang_git_format/LICENSE`; this is not a complete notice review.
The archive and full file inventory were temporary and were not published or
retained by the owner. A matching source declaration does not prove the binary
was built from it, that its contents were linked or shipped, or that any legal
obligations are fulfilled.

For another caller-supplied source archive and independently recorded digest:

```sh
pixi run python scripts/inspect_dependency_source.py \
  --archive /private/source.tar.gz --sha256 <expected-sha256> --root <archive-root> \
  > /private/source-inventory.json
```

The bounded inspector also accepts bzip2 and xz tar archives, rejects links,
special files and unsafe paths, and does not extract or retain source. Archives
containing links cannot be inventoried by this tool without separate review; do
not weaken the checks to force them through. Record the output digest separately
if it will be used as evidence. This is not a source bundle, a closure check or
release clearance. CGAL, Boost and the other sources remain unverified here.

## Selected sysroot and kernel-header RPM checks

The metadata-only `tetraflow-sysroot-rpm-evidence.json` covers the sysroot and
kernel-header packages in the single recorded trial inventory, not every
machine or every build. In hosted runs
[43323781520](https://github.com/Archont561/ODM-conda/actions/runs/43323781520)
and [43323995567](https://github.com/Archont561/ODM-conda/actions/runs/43323995567),
the two selected Conda package archives matched the recorded package hashes;
their embedded recipes declare the same eight binary AlmaLinux RPM inputs.
Those eight downloaded binary RPMs matched their respective recipe SHA256 values.
Their RPM headers name two source RPMs:

| Source RPM named by binary headers | Downloaded SHA256 |
| --- | --- |
| glibc-2.28-236.el8_9.13.src.rpm | `471828a3273bc3ea60ce2d3a67a9bb2ef0921ca9152df3cc15c046dde5bb3263` |
| kernel-4.18.0-513.24.1.el8_9.src.rpm | `4d0d08fc5ff422ac1b959a9d35414c95db9931c58a86776d167ae95dc626169f` |

Both downloaded source RPM hashes matched their entries in the AlmaLinux vault
primary repository metadata; that primary metadata matched the checksum in the
retrieved repomd. This is a same-repository consistency check, **not an
independently authenticated checksum or signature verification**. The RPM
headers were queried, not their payloads extracted or audited. Their claimed
source-RPM names do not prove how the binary RPMs or Conda packages were built,
what sysroot files were used or shipped, or whether the source RPM payloads and
patches satisfy any obligations. The RPMs and repository metadata were
transient and discarded; no owner-retained source bundle was created. Source
closure, signature trust, toolchain patch review, linkage and license review
remain open, and release gates are unchanged.

### RPM signature check and source package listing

A subsequent hosted check
[43324898928](https://github.com/Archont561/ODM-conda/actions/runs/43324898928)
downloaded the same two source and eight binary RPMs, matched the recorded
hashes, and checked their RPM signatures using an isolated RPM database. All
ten reported header and package RSA/SHA256 signatures `OK` under key ID
`ced7258b`. The retrieved AlmaLinux public key had primary fingerprint
`5E9B8F5617B5066CE92057C3488FCF7C3ABB34F8`, matching the primary fingerprint
published in [AlmaLinux release notes](https://wiki.almalinux.org/release-notes/8.3.html);
the retrieved key also contains subkey fingerprint
`BC5EDDCADF502C077F1582882AE81E8ACED7258B`. The key was retrieved over HTTPS;
the fingerprint comparison is the stated trust anchor, not a complete
independent chain-of-custody or legal review. The evidence is recorded in
`tetraflow-sysroot-signature-evidence.json`.

A filename listing (not extraction or content review) reports 873 entries in
the glibc source RPM, including `glibc.spec` and 863 names ending in `.patch`
or `.diff`; the kernel source RPM lists 46 entries, including `kernel.spec`
and three such patch names. These counts do not establish patch applicability,
completeness or the contents of nested source archives. The RPM payloads,
patches and build instructions have not been reviewed or retained. Neither the
signature checks nor the listings verify which files were used, linked or
shipped in the trial, or authorize publication.

### Bounded source RPM payload hashing

In [43326206675](https://github.com/Archont561/ODM-conda/actions/runs/43326206675),
the two source RPMs were downloaded again and matched the previously verified
RPM hashes. Their cpio payloads were streamed without extraction; the probe
rejected unsafe paths, duplicate names, links, special files and oversized
entries, and calculated a SHA256 and size for each regular file. The resulting
summary, spec hashes, nested archive hashes, selected patch hashes and hashes of
the full entry and patch manifests are in `tetraflow-srpm-payload-evidence.json`.
The manifest digest format is documented in that file; the full manifests and
sources were not retained. Counts match the earlier filename listings: 873
entries and 863 patch/diff-named files for glibc, 46 entries and three such
patch files for the kernel. One kernel patch-named file is empty; that alone
does not determine whether or how it is used.

This is an entry-level integrity inventory, not semantic patch review: nested
tarballs were hashed but not opened, spec conditionals and build instructions
were not evaluated, patches were not applied, and actual linkage, corresponding
source completeness and legal obligations remain unverified. No owner-retained
source bundle was created and no release approval is implied.
