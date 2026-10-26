---
id: doc-2
title: Starter validation limits and upstream evidence
type: other
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 19:05'
---
# Known issues and explicit limits

## No complete ODM engine yet

The two starter tools are not enough to process drone photographs. OpenSfM,
OpenMVS, texturing, orthophoto and the final ODM runtime are tracked as Backlog tasks; they do not have placeholder recipes that claim to
produce working packages. NodeODM and GPU variants are also not implemented.

## Pinned FPCFilter sampling without normals

During scaffold validation, an ASCII PLY without normals passed through normally,
but `--radius 0.5` did not reduce the point count for a fixture with near-duplicate
points. Inspection of pinned source commit
`6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b`, `fastsamplefilter.hpp`, shows that the
non-normals branch erases points from a local copy without assigning it back to
`file.points`. No upstream patch is applied by this scaffold.

The tests therefore cover both:

- ASCII/no-normals **pass-through** (all expected points retained).
- ODM-style binary PLY **with normals**, where radius sampling must actually
  reduce the point count on the generated fixture.

This is not a claim that no-normals sampling is correct. Before publishing a
general-purpose FPCFilter package, decide whether to carry a reviewed upstream-
compatible fix, update the pin, or clearly limit/document the supported use case.
If adding a patch, include its license, exact diff and test in source bundles and
reset release gates. Avoid silently changing the selected ODM compatibility set.

Other filtering modes, large datasets, concurrency stress and malformed PLY
handling have not received complete correctness/security review here.

## dem2points fixture scope

The flat 8x8 VRT fixture checks point count, georeferenced positions, elevations
and up-facing normals. It does not comprehensively validate skirt generation,
nontrivial nodata patterns, rotated rasters or all GDAL drivers. Inputs smaller
than the algorithm's border requirements have not been certified safe.

## Native linking and baseline

The initial native recipes use the Conda GNU toolchain and a glibc 2.28 sysroot.
The runtime solver may impose a higher minimum through dependency builds. A
successful test on this sandbox is not certification on older distributions.

An `_openmp_mutex` overdependency warning can be emitted through libgomp's
run_exports. It is not hidden as an error-free build log. Artifact checks still
require libgomp/libgcc/libstdcxx declarations and resolved installed linkage.

## License and source review

The starter code records conservative `GPL-3.0-only` expressions pending review
of upstream grants/version choices. The source bundler supports only the current
single-archive sources, with vendored code included. It rejects submodules and
undisclosed CMake downloads in enabled targets. FPCFilter records its disabled
`test/` tree explicitly: the test-only GoogleTest fetch is not executed, while the
entire test tree is still present in the archived source. Planned multi-project components need a source-graph extension,
not a bypass of that rejection.

Source completeness and license compatibility are human review gates, not claims
proven by the static checks. All public release gates remain false in the scaffold.
