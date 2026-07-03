# Changelog

All notable changes to this project are documented here. Versions track the
bundled ICU release: `<ICU major>.<ICU minor>.<package revision>`.

## 78.3.0 (unreleased)

Bundles **ICU 78.3** and **PyICU 2.16.2** (previously ICU 78.2 / PyICU 2.16).
ICU 78.3 includes CLDR 48.2 fixes and time-zone data 2026a.

### Packaging

- Versions and source checksums now live only in `pyproject.toml`
  (`project.version` and `[tool.icukit-pyicu]`); CI reads them instead of
  hardcoding, and a CI guard fails on any hardcoded version literal in the
  workflow.
- `pyproject.toml` now builds a valid wheel with `python -m build`
  (`pip install .` previously failed on a missing `icu/` package directory).
- The published wheel is assembled with standard tooling (`wheel unpack` /
  `wheel pack`) instead of hand-written `METADATA`/`WHEEL`/`RECORD`; wheel
  metadata (including the README long description) is generated from
  `pyproject.toml`.
- Every wheel is validated with `twine check` in CI before upload.
- The macOS platform tag is now honest: `MACOSX_DEPLOYMENT_TARGET=11.0` is set
  when building ICU and PyICU, the tag is derived from the delocate output
  rather than hardcoded, and CI asserts no bundled dylib requires a newer macOS.
- Source integrity is verified: the ICU tarball is checked against a pinned
  SHA-256, and PyICU is downloaded with `--require-hashes`.
- License compliance: the wheel now ships ICU's `LICENSE-ICU` (Unicode-3.0)
  alongside `LICENSE` (MIT) and declares the SPDX expression
  `MIT AND Unicode-3.0`.
- Static ICU archives (`*.a`) are no longer bundled, reducing wheel size;
  shared libraries and dev headers remain.

### Platforms

- Added Linux **aarch64** wheels (manylinux) to the build matrix.

### CLI and helpers

- `icukit-config --libs` now emits the full link line
  (`-L<dir> -licui18n -licuuc -licudata`), `--cflags` emits `-I<dir>`, and a new
  `--version` flag prints the package version.

### Tests

- Added tests for the `icukit_pyicu` helpers and the `icukit-config` CLI.
- Added a CI smoke test that compiles and runs a C++ program against the bundled
  ICU headers/libraries.
- `test_version` no longer hardcodes the ICU major version.

### CI hygiene

- Pushes to `main` run a 2-wheel smoke matrix; the full matrix runs on tags,
  releases, and manual dispatch. Added a `concurrency` group so superseded runs
  are cancelled.
