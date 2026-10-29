# mvs-texturing-odm: preliminary license review

Status: evidence for human review, **not** legal advice, license approval, or
permission to publish. All release checks remain false. This review concerns
version `0.0.0.dev20250818`; build 1 adds a previously omitted notice.
Native CI [40742094824](https://github.com/Archont561/ODM-conda/actions/runs/40742094824)
validated build 1's package tests, fresh-environment retest, audit and source
bundling. Build 2 adds a fail-closed GNU link-map check and passed native CI
[40746814931](https://github.com/Archont561/ODM-conda/actions/runs/40746814931). Neither result approves licenses or proves source
completeness.

## Reviewed evidence and provisional obligations

The five exact archives in `research/source-graphs.json` were downloaded,
SHA-256 checked, staged, and the 20 listed files verified with
`scripts/verify_staged_notices.py`. The following is a conservative preliminary
source-level assessment, not a complete compile/link or legal analysis.

| Source | Evidence and review implications |
| --- | --- |
| Texturing, MVE, mapmap, rayint | Root BSD-3-Clause notices identify different copyright holders; preserve each notice and disclaimer, including in binary-distribution materials. |
| MVE `libs/mve/image_exif.cc` | Contains separate Mayank Lahiri / Simon Fuhrmann copyright and two-condition BSD-style terms, including binary notice requirements. It is built into the MVE static library by the upstream CMake glob; whether its object enters the final executable has not been proven. Build 1 conservatively carries the complete file verbatim and adds `BSD-2-Clause` to the preliminary expression. Classification is subject to review. |
| mapmap `ext/dset` | Separate zlib-style notice requires source-notice retention and marking altered versions. The recipe preserves the notice and identifies the patched sources. |
| Eigen | `COPYING.README` describes MPL-2.0 and additional BSD/LGPL code. Texturing defines `EIGEN_MPL2_ONLY`; that is not a determination that all source-archive content is MPL-only. Retain notices and assess MPL source/modification obligations for covered files. The full Eigen source archive also contains GPL, LGPL, BSD and MINPACK license texts; source-bundle review cannot be limited to the compiled subset. |
| Eigen `Eigen_Colamd.h` | Carries MPL-2.0 plus a University of Florida permission/availability notice. Preserve the full file and make its notice accessible as stated; the custom `LicenseRef-COLAMD` is provisional. |
| Eigen SuperLU-derived headers | Carry MPL-2.0 and permission notices requiring retained notices and modification markings. The inventory preserves identified headers verbatim; `LicenseRef-SuperLU` is provisional and not proof that all applicable notices have been found. |
| Packaging code | MIT notice is included separately. |

The current conservative expression is `BSD-3-Clause AND BSD-2-Clause AND Zlib
AND MPL-2.0 AND LicenseRef-COLAMD AND LicenseRef-SuperLU AND MIT`. It describes
preliminary package-level evidence, not the license of every file in the five
full source archives or separately installed conda dependencies. A qualified
reviewer must confirm the SPDX identifiers, custom references and their scope.

## Important unresolved issues

1. **MVE non-free disclaimer:** MVE's root license warns that
   `libs/sfm/sift.cc` and `libs/sfm/surf.cc` may be patented or otherwise
   restricted. The recipe builds the `mve_sfm` static library because upstream
   `FindMVE.cmake` requires it; that library's CMake glob includes both files.
   The texrecon target links MVE's `mve` and `mve_util` libraries, not the sfm
   library directly. The build 1 CI log confirms both `sift.cc.o` and
   `surf.cc.o` were compiled into `mve_sfm`; this is not proof they entered
   `texrecon`. The CI output lacks a final link map, and the archived binary
   was not independently inspected in this review. Build 2 asks GNU ld for a
   map of the texrecon link and fails if it is missing, incomplete, or names
   the sfm archive or SIFT/SURF objects. A synthetic GNU link-map test passed. Build 2 was subsequently run natively in
   [run 40746814931](https://github.com/Archont561/ODM-conda/actions/runs/40746814931),
   which passed the build, including the fail-closed link-map check, fresh retest,
   audit and source bundling. The build map was not independently inspected for this review. Even a passing check cannot rule out
   equivalent code elsewhere or resolve the separate source-archive and patent
   questions. No patent analysis has established what rights apply.
   The original MVE archive containing both files is included in the source
   bundle. Preserve the disclaimer and obtain appropriate review; do not infer
   either patent infringement or patent expiration from this notice.
2. Complete the source and notice inventory, including all statically linked
   objects, Eigen template instantiations, and full source archives. A hash or
   successful source-bundle task verifies bytes, not redistribution rights or
   completeness. Confirm the separate `image_exif.cc` notice and classification.
3. Review licenses and notices for the **actual resolved runtime dependencies**
   (including TBB, libjpeg-turbo, libpng, libtiff, zlib and compiler runtimes),
   including obligations in any distributed environment. They are separate conda
   packages, not automatically covered by this recipe's expression.
4. Confirm how MPL covered source and modifications will be made available in
   the actual distribution, the source-offer URL and retention policy, and
   whether bundled source archives and all assets can be redistributed.
5. Have the owner or qualified reviewer decide and record license approval; then
   independently validate native build 2, source completeness, and the other
   release gates. No gate changes or release are authorized by this document.

## Runtime dependency evidence (preliminary)

The build 1 [fresh-environment retest](https://github.com/Archont561/ODM-conda/actions/runs/40742094824/job/123006108578)
resolved `tbb 2023.1.0 haa8c3ee_2`, `libjpeg-turbo 3.2.1 h7cc23a3_0`,
`libpng 1.6.59 h922cc85_0`, `libtiff 4.7.2 hcc2c06a_1`, `libzlib 1.3.2
h25fd6f3_3`, and `libgcc`, `libgomp` and `libstdcxx` 16.2.0. This was a
**test** environment, also containing Python and transitive dependencies; a
future solve can differ. Its package list is not an inventory of all ELF
linkage. The native build compiler was GCC 14.4.0, not 16.2.0.

The following are **upstream files at matching version tags**, identified by
immutable commit and SHA-256, not verified copies of the actual conda-forge
package metadata or notices. They are starting points for review, not a
complete runtime license inventory:

| Runtime source evidence | SHA-256 | Preliminary review note |
| --- | --- | --- |
| [oneTBB 2023.1.0 LICENSE.txt](https://github.com/oneapi-src/oneTBB/blob/3046c8b0c29df995980003ea24f4d78c80ec0c8d/LICENSE.txt) | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | Apache 2.0 text. Verify applicable package notices, modification statements and source provenance. |
| [libjpeg-turbo 3.2.1 LICENSE.md](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/7b4993786d856cbccabfc0ed2f923ba000e326cc/LICENSE.md) and [README.ijg](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/7b4993786d856cbccabfc0ed2f923ba000e326cc/README.ijg) | `ba6bceebcba0fdd35488477c2cca8c4632ce82c74dbfbc87d886ce6fc4433579`; `75815e3bf6484201a3c3d17a1bbf10f2e8e3237f84df10a2357ea896db2a81d6` | Upstream describes IJG and BSD-style terms; IJG's executable-distribution terms call for the Independent JPEG Group acknowledgement in accompanying documentation. Assess whether and where it applies to the intended distribution. |
| [libpng 1.6.59 LICENSE](https://github.com/pnggroup/libpng/blob/cd952f49f95bb27154ae77dbb103032d95f6e580/LICENSE) | `bdb0a645ea18c60507d0368379b1ac5474b92255fcc2d115e07486a7672ba526` | PNG reference library license v2; the file also documents earlier licensing and notes some contributed files differ. |
| [libtiff 4.7.2 LICENSE.md](https://github.com/libsdl-org/libtiff/blob/d01a94be176f5f6a87f7ee1c0b32e65416aa2b4d/LICENSE.md) | `0e27c2382d7b8147972bbb746e04059a1152c8d0fda9d03ef1399d1a433c4ade` | Includes libtiff's notice plus additional component notices; review the complete file and the actual package. |
| [zlib 1.3.2 README](https://github.com/madler/zlib/blob/da607da739fa6047df13e66a2af6b8bec7c2a498/README) | `4026d921213bb2e311d8d42b44ef53361c102d5d45ae32f93f8e52eaee8d068f` | Contains the zlib notice; verify actual packaged notices and source. |
| GCC 16.2.0 [runtime exception](https://github.com/gcc-mirror/gcc/blob/78d4ac73dd391005b895a6148cd9831e28e1208b/COPYING.RUNTIME) and [GPL text](https://github.com/gcc-mirror/gcc/blob/78d4ac73dd391005b895a6148cd9831e28e1208b/COPYING3) | `9d6b43ce4d8de0c878bf16b54d8e7a10d9bd42b75178153e3af6a815bdc90f74`; `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903` | The runtime exception exists upstream; verify each installed runtime's actual license, exception applicability and distribution obligations rather than assigning this text to all compiler components. |

The retest also included transitive packages such as libhwloc, libxml2,
libwebp-base, libdeflate and lerc. Their package-specific terms and the
Python-only test dependencies have not been reviewed. The non-published CI
artifact ID is `12840460918`, artifact ZIP SHA-256
`c81c46c7f33fbdfb6fee1eef5269710bbdf7a8b83e91839e577fe1f8c0d379b1`; the
CI-created source bundle SHA-256 is
`900578aae61f9baa2129e28afb24c9fb1729eef07edd68937970ec3f07746c5c`.
These hashes identify evidence, not approval or a guarantee of future availability.


## Independent build 2 artifact inspection (2026-10-29)

Temporary read-only [inspection run 40847899604](https://github.com/Archont561/ODM-conda/actions/runs/40847899604)
independently downloaded artifact `12841144045`, verified ZIP SHA256
`5a92c91c65b56433766eddb739f5db488d4c0cf8403647274aee262c26bdd899`,
re-audited the package and passed an additional fresh isolated retest. Package
`mvs-texturing-odm-0.0.0.dev20250818-h873e7db_2.conda` SHA256
`af287aa4cb94f5b34e1e55d202e428123a1cc6d8ddc505ee74717e23ed92c4bc`; source
bundle SHA256 `20f2c19760b9576c0163795adf82bef36d8460e1eadcae92f78d94efd9888154`,
with 196 manifest-listed file hashes verified and packaging commit
`902550d4f7438d382a2288e064b185a6834e53cf`. The older manifest has no dirty
worktree marker. Package RPATH is `$ORIGIN/../lib`; ELF NEEDED includes libjpeg,
libpng16, libtiff, TBB and standard runtimes. It has 21 license metadata entries;
counting them does not prove notice completeness. The original build guard passed
for named SIFT/SURF inputs, but the raw link map was not retained and is not
independently inspected. Source rights, patent questions, complete transitive
notices and ABI/legal review remain open. The temporary workflow and helper were
removed; this inspection does not authorize redistribution.
