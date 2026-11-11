# Pillow JPEG XL project grant: bounded review

## Reviewer conclusion

The strongest newly identified evidence is a **later upstream maintainer-authored
project metadata declaration of `GPL-3.0-or-later`**. It makes GPL-3.0-or-later
a well-supported interpretation of the maintainer's later project-level intent,
not a proven grant for every file in the pinned 1.3.4 sdist. The pinned release
itself refers to the GPL v3 license text without specifying an SPDX expression
or an explicit per-project “or later” grant. The later declaration did not
change the root license text, but it followed 1.3.4 and does not expressly say
that it clarifies that release or all contributors' rights.

**Recommendation:** retain `LicenseRef-Unreviewed` and keep publication gated
until the owner/qualified reviewer decides whether the evidence is sufficient,
or obtains a maintainer clarification specifically covering version 1.3.4 and
its contributors. This is a technical evidence review, not legal advice, a
license approval, a comprehensive rights determination or permission to publish.

## Chronology and evidence

1. [Initial commit `54abc4e`](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/54abc4e23dc7a0f36ff89c10c28e49a40dd872c3)
   (2023-09-26) has an MIT root license naming Isotr0py. A
   [September 2024 issue](https://github.com/Isotr0py/pillow-jpegxl-plugin/issues/59)
   questioned the interaction with GPL-licensed `jpegxl-rs`. The maintainer
   [responded](https://github.com/Isotr0py/pillow-jpegxl-plugin/issues/59#issuecomment-2323668552):
   “I will correct the project license with the GPLv3 same as jpegxl-rs.”
   [Commit `284a7f0`](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/284a7f01124159d5da8de52a107c4da56fb66ed0)
   changed the root LICENSE from MIT to GPL v3 text, with the message “Update
   LICENSE to GPLv3.0”. The response and message do not themselves specify
   only-versus-or-later or establish each contributor's grant.
2. The pinned [1.3.4 tag commit `1aaa8a3`](https://github.com/Isotr0py/pillow-jpegxl-plugin/tree/1aaa8a3142aa1d5c3f77e8410e1ddda2d26666ed)
   is dated 2025-07-03. Its `pyproject.toml` says
   `license = { file = "LICENSE" }`; its Cargo manifest has no `license`
   field. The hash-verified PyPI sdist
   `8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e`
   has `PKG-INFO` SHA-256
   `8641fec5f0ea9baf001211ba79011341b762326cf449d2fcfb98bb7958520995`;
   that metadata has `License-File: LICENSE`, but no `License-Expression` or
   `License` field. The root LICENSE SHA-256 is
   `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.
   The general GPL license text's example of applying “version 3 ... or any
   later version” is not itself a separate project-specific grant.
3. On 2025-11-26, another participant in that issue
   [suggested](https://github.com/Isotr0py/pillow-jpegxl-plugin/issues/59#issuecomment-3580097518)
   using `GPL-3.0-or-later` to address PyPI metadata display. The maintainer
   authored and merged [PR #131](https://github.com/Isotr0py/pillow-jpegxl-plugin/pull/131),
   resulting in [commit `f913590`](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/f913590267ea792f57490d544697868242b59f75)
   on 2025-12-04. It changes `pyproject.toml` from the license-file reference
   to `license = "GPL-3.0-or-later"` and `license-files = ["LICENSE"]`; the
   commit message says “Update license view on pypi” and links to the
   suggestion. Its Cargo manifest identifies project version 1.3.5. Commit
   `1aaa8a3` is an ancestor of `f913590`, and the root LICENSE at both commits
   has the same SHA-256 above. The later metadata is persuasive project-level
   context, but the stated aim was metadata display, not an explicit statement
   about the earlier release or authority over third-party material.

The 1.3.4 sdist `PKG-INFO` and upstream Git history were inspected separately;
the previous [source comparison](pillow-jxl-release-review-2026-11-11.md)
records the matching Git tag and sdist files. Hashes identify bytes, not the
identity or legal authority of contributors.

## Contributors and boundaries

The pinned history attributes changes in retained plugin and Rust source files
to several contributors besides the maintainer. For example, Javier Martin's
[quality work](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/911152ff578f0df92b7d0d417fd9114993e36f73)
predates the 2024 license change; Rapha S's
[metadata change](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/23d094aec7b516cab408452d01f380c763180e2f),
Maël Kerbiriou's [threading change](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/95542a18799fdeb45be1d92ada8b68489cf119aa),
and Disty0's [EXIF change](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/ae9ca9151db99d72bbb6a7d09570bab0067806ad)
follow it. `git blame` at the tag attributed lines in the retained plugin file
and/or Rust files to these authors. Commit authorship and blame are limited
provenance signals: they do not establish authorship of all code, applicable
individual grants, contributor agreements or permission to relicense.

The dependency `jpegxl-rs` and `jpegxl-sys` locked versions have separate
explicit GPL-3.0-or-later declarations and license text, documented in the
[release review](pillow-jxl-release-review-2026-11-11.md). That does not
independently establish the project's own grant, determine combined-work
obligations, or clear the Rust/native closure. Likewise, excluded fixtures,
third-party notices, and corresponding-source completeness remain separate
questions; see the [source trial](pillow-jxl-source-offer-preparation-2026-11-11.md).

## Decision questions

- Ask the maintainer whether the `GPL-3.0-or-later` expression is intended to
  cover the project code in version 1.3.4, including contributions before and
  after the license change, and whether they know of separate terms or relevant
  contributor agreements. Their response may still require independent review.
- Have the owner/qualified reviewer assess that answer and provenance, the
  original MIT-era grant and later project declaration, then decide the exact
  release metadata and whether any permissions are missing. Do not treat this
  document as a request already sent or an approval.
- Separately assess dependencies, notices, source delivery and image rights;
  validate the exact release artifact and obtain the relevant owner approvals.
  No code, dependency, license metadata, release gate, or channel publication
  is changed by this review.
