# Build architecture

This document explains how the published wheels are produced, and why. The build
lives entirely in `.github/workflows/build.yml`; the repository source is just
the `icukit_pyicu` helper package, tests, and metadata.

## Goal

`pip install icukit-pyicu` should give a working `import icu` (PyICU) with no
system ICU installed, plus the ICU dev headers/libraries and a pkg-config-style
CLI for building other projects against the same ICU.

A single wheel therefore contains three things:

1. `icu/` — the PyICU extension module and the ICU **runtime** shared libraries
   it links against (vendored by delocate/auditwheel).
2. `icukit_pyicu/` — the repo helper package plus the ICU **dev** tree
   (`include/`, `lib/`, `bin/`) for linking other code.
3. `icukit_pyicu-<version>.dist-info/` — standard wheel metadata.

## Single source of truth

`pyproject.toml` holds everything version-related:

- `project.version` — the package version (`<ICU major>.<ICU minor>.<rev>`).
- `[tool.icukit-pyicu]` — the ICU and PyICU versions to build, plus the SHA-256
  of each upstream source archive.

The `config` job reads these with `tomllib` and exposes them as job outputs. A
guard step fails the build if a bare version literal appears in the workflow, so
the pins cannot silently drift back into the YAML.

To bump: edit `version` and the four `[tool.icukit-pyicu]` values together, then
verify the checksums (see below), and update `CHANGELOG.md`.

### Recomputing checksums

```bash
# ICU source
curl -L https://github.com/unicode-org/icu/releases/download/release-<VER>/icu4c-<VER>-sources.tgz \
  | shasum -a 256
# PyICU sdist (from PyPI JSON)
curl -s https://pypi.org/pypi/PyICU/<VER>/json \
  | python3 -c 'import json,sys; [print(u["digests"]["sha256"]) for u in json.load(sys.stdin)["urls"] if u["packagetype"]=="sdist"]'
```

## Pipeline (per matrix entry)

1. **Download + verify ICU**, check against the pinned SHA-256, extract.
2. **Build ICU from source** (`--enable-static --enable-shared`, samples/tests
   disabled) into `/tmp/icu-dist`. On macOS, `-headerpad_max_install_names` is
   passed so delocate can rewrite install names, and `MACOSX_DEPLOYMENT_TARGET`
   is set so the binaries' minimum-OS matches the wheel tag.
3. **Download + verify PyICU** with `pip download --require-hashes`.
4. **Build PyICU** against the just-built ICU (`-std=c++17`, ICU on the include
   and library paths). This yields a raw `pyicu-*.whl` whose `icu/*.so` links
   against the ICU libs in `/tmp/icu-dist`.
5. **Vendor the ICU runtime** into the wheel: `delocate-wheel` (macOS) or
   `auditwheel repair` (Linux) copies the ICU shared libraries into the wheel
   and rewrites the extension's load paths to find them relatively.
6. **(macOS) Verify deployment target** — assert with `vtool` that no vendored
   dylib requires a newer macOS than the wheel claims.
7. **Assemble the final wheel** (see below).
8. **Validate** with `twine check` (hard gate) and `check-wheel-contents`
   (advisory — the vendored libraries are expected).
9. **Test**: install the wheel, run the pytest suite, and compile+run a C++
   program against the bundled dev tree to prove linkage works.

## Wheel assembly (step 7)

Earlier versions hand-wrote `METADATA`, `WHEEL`, and `RECORD` and re-zipped the
tree. That was fragile (a wrong hash or stray file produced a corrupt or
unverifiable wheel) and duplicated what packaging tools already do. The current
approach uses only standard tools:

1. Copy the ICU dev tree into `icukit_pyicu/{include,lib,bin}` and delete static
   `*.a` archives (consumers link the shared libraries; the archives roughly
   double the size).
2. `python -m build --wheel` produces `icukit_pyicu-<ver>-py3-none-any.whl` with
   correct, complete metadata generated from `pyproject.toml` (long description
   from the README, entry points, `BSD-2-Clause AND Unicode-3.0`, both license files).
3. `wheel unpack` both that wheel and the delocate/auditwheel-repaired PyICU
   wheel, then copy the PyICU wheel's `icu/` package and its `*.libs` directory
   into the helper tree. Only the helper's `dist-info` is kept, so no leftover
   PyICU metadata or license ends up mislabeled as ours.
4. Rewrite the `WHEEL` file to be a platform wheel (`Root-Is-Purelib: false`)
   and set the tag derived from the delocate/auditwheel output filename (never
   hardcoded — that is what keeps the platform tag honest).
5. `wheel pack` regenerates `RECORD` with correct hashes and names the wheel
   from the metadata and tag.

## Matrix and triggers

- Push to `main`, tag pushes (`v*`), and releases: the **full** matrix
  (macOS arm64 + Linux x86_64/aarch64 × Python 3.9–3.14) — `main` is always
  fully validated.
- Push to a feature branch, or a plain `workflow_dispatch`: a 2-entry **smoke**
  matrix (one macOS, one Linux) to catch breakage cheaply. Dispatch with
  `full=true` to force the full matrix.
- Publishing to PyPI (trusted publishing / OIDC) happens **only** on `release`
  events.

A `concurrency` group cancels superseded runs on the same ref.

## Validating a change to this workflow

Because the pipeline compiles ICU from source, it cannot be fully run locally.
Before relying on a change:

1. Trigger `workflow_dispatch` (runs the full matrix) or push to a branch, and
   let at least one macOS and one Linux entry complete.
2. Confirm the build is green, `twine check` passes, the C++ smoke test passes,
   and the wheel tag is what you expect (`unzip -p dist-final/*.whl '*/WHEEL'`).
3. On macOS, confirm `minos` on the bundled dylibs is `11.0`
   (`vtool -show-build ...` / `otool -l`); on Linux, confirm the intended
   manylinux tag (`auditwheel show`).
4. Do not create a release while iterating — that would publish to PyPI.
