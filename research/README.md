# Experimental source staging

`source-graphs.json` is preliminary research for the six selected components,
not a recipe, completeness attestation, or release authorization. The plans
record immutable archives observed during research; mutable ODM references were
resolved at the time recorded in their Backlog tasks. They must be reviewed
again when selecting final release sources.

To reproduce an isolated staging smoke test (requires network access to GitHub
or a pre-populated hash-checked cache):

```sh
python scripts/stage_sources.py --component opensfm --output /tmp/opensfm-source
```

Supported experimental plan names are `dem2mesh`, `poissonrecon`, `renderdem`,
`opensfm`, `openmvs`, and `mvs-texturing`. The output directory must not exist.
Each source archive is rehashed, and extraction rejects links, unsafe paths and
nonempty staging destinations. Declared `.gitmodules` paths must be explicitly
staged; gitlink commits must still be verified separately against the Git tree,
because a source archive cannot establish them. With a local Git repository
containing the pinned primary commit, run:

```sh
python scripts/verify_gitlinks.py --component opensfm --repository /path/to/opensfm-git
```

The verifier compares all primary-tree gitlink paths and revisions with entries
marked `gitlink: true` in the plan, rejecting missing, unexpected or changed
links. It does not verify nested repository gitlinks or equivalence of the
archive with the Git tree, nor does it prove source or license completeness. The plans contain only sources
identified so far. The plan and this file are included in packaging source bundles
alongside the staging scripts; their presence does not authorize release. In particular, the staged mvs-texturing tree still contains upstream
ExternalProject download commands, and its MVE source is in a non-default path.
The Eigen archives use a GitHub mirror and are not the original GitLab
archive bytes. The texturing plan pins the exact GitLab 3.3.2 tag commit
`477d1e81928a8514d2cca6a6e1e7e478eecd8634`, which is also available on the
GitHub mirror. Its earlier GitHub tag resolves to a different commit with an
extra `.hgtags` file; the earlier local texrecon build used that older plan.
For the openMVS Eigen pin, both hosts identify the same Git commit. Original
GitLab tarball bytes, full notices and network-isolated builds remain unverified. The production recipes, builder, corresponding-
source bundler and release machinery continue to reject unsupported graphs.

For a **research-only** archive containing the plan, all planned upstream
archives and packaging sources including the experimental patch:

```sh
python scripts/bundle_staged_sources.py --component mvs-texturing --output /tmp/texturing-research.tar.gz
```

The helper verifies hashes and stages the graph before writing a deterministic
archive and manifest. It refuses to overwrite a destination. This archive is
not a release source bundle or a source-completeness certification.

`mvs-texturing-notices.json` records hashes of 19 preliminary notice-bearing
files. To verify them against the matching staged tree, run:

```sh
python scripts/verify_staged_notices.py --tree /tmp/texturing-source
```

This checks the listed bytes only; it does not establish a complete inventory
or decide license obligations.

`patches/mvs-texturing-offline.patch` is a configure-only experiment against
the pinned mvs-texturing archive. It replaces active ExternalProject targets
with checks for staged sources and removes `-march=native`. Configuration was
initially smoke-tested with temporary dependency stubs. A subsequent local
research build linked `texrecon` against locally built MVE libraries and the
restored TBB runtime, using matching-version upstream TBB headers. This was not
a network-isolated or installed-package validation. A real TBB development
package, complete source and license review, native CI build and installed-prefix
functional test remain required.

`patches/mve-baseline-cpu.patch` is a research patch against the pinned MVE
archive that removes its unconditional GNU `-mpopcnt` option. Together with
the texturing offline patch, a local GCC 12 build using `-march=x86-64
-mno-popcnt` produced `texrecon` and passed the generated-scene fixture. The
70 MVE object files and the resulting executable contained no POPCNT
instructions in an `objdump` inspection; 25 texturing compile commands also
used the requested baseline flags. This covers only the inspected build output,
not its dynamically linked libraries, other compiler instructions, an isolated
Conda build or a package audit. Both patches remain research-only.

A generated-scene **research-only** texrecon fixture is available after building
an executable from the pinned sources:

```sh
python scripts/texrecon_fixture.py --executable /absolute/path/to/texrecon
```

It checks the output geometry, texture references and PNG structure. The fixture
skips both seam-leveling stages and inherits the caller's runtime library path.
A successful run against a research binary is not package validation.

For an OpenSfM tree with its eight native bindings already built, a preliminary
import and geometry smoke test can be run with:

```sh
python scripts/opensfm_fixture.py /absolute/path/to/opensfm-source-root
```

It imports the bindings from that exact tree, checks an equatorial ECEF
conversion and an identity pose. This is not an installed package, dataset,
source-completeness or release test.

`patches/opensfm-ceres-config.patch` is a research patch that selects the Ceres
CMake package and propagates its target requirements to native-module consumers.
It applies to the pinned OpenSfM source and was tested in a mixed local
GCC/Pixi environment against Ceres 2.2 and Python 3.12; it is not part of a
production recipe and has not been validated with an isolated package build.
