# mvs-texturing-odm: preliminary license review

Status: evidence for human review, **not** legal advice, license approval, or
permission to publish. All release checks remain false. This review concerns
version `0.0.0.dev20250818`; build 1 adds a previously omitted notice. The
successful native CI run [40740410329](https://github.com/Archont561/ODM-conda/actions/runs/40740410329)
validated build 0, not this revised build 1.

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
   library directly, but no final link-map or patent analysis has established
   whether any relevant implementation is incorporated or what rights apply.
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
   independently validate native build 1, source completeness, and the other
   release gates. No gate changes or release are authorized by this document.
