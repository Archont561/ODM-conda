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
