# icukit-pyicu — Review Findings & Execution Plan

> Audience: an AI agent (or human) executing improvements to this repo.
> Every finding below was verified against the actual files (paths/lines cited) or
> empirically (commands shown). Do the phases in order; each task has acceptance
> criteria. Follow the Validation Protocol before touching the full CI matrix.

## 1. What this project is

`icukit-pyicu` publishes pip wheels that bundle a **source-built ICU** together with
**PyICU**, so `pip install icukit-pyicu` gives a working `import icu` with no system
ICU required. The wheels additionally ship ICU dev headers/libs/binaries under the
`icukit_pyicu` package, exposed via helper functions (`get_include()`, `get_lib()`,
`get_bin()`) and an `icukit-config` CLI (pkg-config-style).

**Key architectural fact:** the published wheel is NOT produced by
`pyproject.toml`/setuptools. The GitHub Actions workflow
(`.github/workflows/build.yml`) builds ICU from source, compiles PyICU against it,
runs delocate (macOS) / auditwheel (Linux) to vendor the shared libs, then
**hand-assembles** the final wheel: unzip → rename dist-info → write METADATA/WHEEL/
RECORD/entry_points by heredoc → re-zip. The repo's `pyproject.toml` is effectively
dead config. The git history is a trail of hard-won rpath/linker fixes — read it
before changing link/bundle steps.

Repo inventory (9 files): `pyproject.toml`, `README.md`, `LICENSE`, `.gitignore`,
`icukit_pyicu/{__init__.py,__main__.py}`, `tests/{__init__.py,test_icu.py}`,
`.github/workflows/build.yml`.

Current state: version `78.2.1` = ICU 78.2 + PyICU 2.16, published to PyPI on
GitHub release events via trusted publishing (OIDC). Matrix: macOS arm64 + Linux
x86_64 × Python 3.9–3.14 (12 wheels).

## 2. Verified facts (checked 2026-07-03)

| Fact | How verified |
|---|---|
| `pip install .` fails: `error: package directory 'icu' does not exist` | Ran locally; setuptools aborts during metadata generation |
| Latest ICU is **78.3** (2026-03-17; CLDR 48.2 fixes, tzdata **2026a**) | unicode-org/icu releases |
| Latest PyICU is **2.16.2** (2026-03-20; 2.16.1 and 2.16.2 are bugfix releases) | PyPI |
| ICU release assets: `icu4c-X.Y-sources.tgz` + `.md5` + GPG `.asc` under tag `release-X.Y` | GitHub API for release-78.3 (workflow URL pattern at build.yml:55 is correct) |
| delocate ≥0.11 validates grafted-lib deployment target vs wheel tag and respects `MACOSX_DEPLOYMENT_TARGET` | delocate docs / cibuildwheel docs |
| The heredoc-indentation `sed` at build.yml:221 is a **no-op** (YAML block scalars already strip the indent) — not a bug, but dead code | Read of YAML block structure |

## 3. Findings

Severity: **H**igh (correctness/shipping risk), **M**edium, **L**ow.

| ID | Sev | Location | Finding |
|----|-----|----------|---------|
| F1 | H | `pyproject.toml:31,34` | Declares packages `["icu", "icukit_pyicu"]` and package-dir `icu = "icu"`, but no `icu/` dir exists in the repo. `pip install .` / `python -m build` fail immediately (verified). The file misleads contributors and tooling; the real wheel ignores it. |
| F2 | H | `pyproject.toml:7`, `build.yml:6-7,193,200,271` | Version `78.2.1` hardcoded in 4 places plus separate `ICU_VERSION`/`PYICU_VERSION` env vars. A bump requires editing all of them correctly or wheels ship mislabeled. |
| F3 | H | `build.yml:150-275` | Final wheel is hand-assembled (unzip → mutate → hand-write RECORD → `zip -rq`). Reinvents `wheel unpack`/`wheel pack`; any stray file or hash slip silently produces a corrupt/unverifiable wheel. Biggest maintenance risk in the repo. |
| F4 | H | `build.yml:100-106,156-158` | **macOS deployment-target mismatch.** `MACOSX_DEPLOYMENT_TARGET` is never set. ICU dylibs get clang's default min version (= the macos-14 host), while `_PYTHON_HOST_PLATFORM` claims `macosx-11.0-arm64` and the final tag is hardcoded `macosx_11_0_arm64` (build.yml:158) — overriding whatever delocate determined. The wheel may claim macOS 11 compatibility while containing binaries requiring 14. Users on Big Sur–Ventura arm64 get import-time failures. |
| F5 | H | `build.yml:197-219` | Hand-written METADATA heredoc diverges from `pyproject.toml`: truncated description, missing classifiers, will drift on every metadata change. PyPI page shows the heredoc stub, not the README. |
| F6 | M | `build.yml:55-57,91` | No integrity verification of downloads: ICU via bare `curl -L`, PyICU via `pip download` without hashes. A tampered/corrupted source would be built and published silently. ICU publishes `.md5`/`.asc`; pin a locally computed SHA-256. |
| F7 | M | `build.yml:6-7` | Pinned versions are behind upstream: ICU 78.2 → **78.3** (includes tzdata 2026a — timezone correctness matters for a date/time library) and PyICU 2.16 → **2.16.2** (two bugfix releases). |
| F8 | M | `icukit_pyicu/__main__.py:22-24`, `README.md:36` | `icukit-config` is advertised as pkg-config-like but `--libs` emits only `-L<dir>` (no `-licui18n -licuuc -licudata`) — users get link errors following the README. No `--version` flag either. |
| F9 | M | `build.yml:182-185` | ICU shared libs are bundled **twice**: once by delocate/auditwheel into the `icu` package, again via wholesale `cp -R /tmp/icu-dist/lib` (incl. static `.a` archives) + `bin/` into `icukit_pyicu/`. Likely doubles wheel size (~30 MB+ of ICU data/libs) × 12 wheels. |
| F10 | M | wheel dist-info | **License compliance:** wheel bundles ICU binaries but ships only `License: MIT` in the hand-written METADATA. ICU's Unicode-3.0 license text is not included in the wheel; the renamed PyICU dist-info may retain PyICU's own LICENSE, mislabeled as ours. |
| F11 | M | packaging policy | No sdist is published; platforms outside the 12-wheel matrix get "no matching distribution found" with no explanation. (Probably correct to stay wheels-only — but must be an explicit, documented decision.) |
| F12 | L | `tests/test_icu.py:8` | `assert icu.ICU_VERSION.startswith("78.")` — false-fails on the next ICU major; doesn't validate against the version the build targeted. |
| F13 | L | tests / CI | Nothing exercises the headline dev feature: no test of `icukit_pyicu` helpers, the `icukit-config` CLI, or actually compiling+linking a C++ program against the bundled headers/libs. |
| F14 | L | `pyproject.toml:10-11,14-21` | `license = {file=...}` is deprecated (PEP 639); missing per-version Python classifiers; author email `keinlenzo@gmail.com` looks like a typo for "kevinlenzo" — **confirm with owner before publishing anything**. |
| F15 | L | `build.yml:10-13` | Every push to main runs the full 12-job source-build matrix (~30-60 min each); no `concurrency` group, so pushes stack builds. |
| F16 | L | matrix | No Linux aarch64 (GitHub now has free `ubuntu-24.04-arm` runners for public repos), no macOS x86_64, no Windows. May be intentional — README should say so. |
| F17 | L | `build.yml:221`, Linux wheel | Cosmetics/debt: no-op `sed` (verified above); Linux wheel retains auditwheel's `pyicu.libs/` dir name inside an `icukit_pyicu` wheel (harmless — rpath is `$ORIGIN`-relative — but confusing). |
| F18 | L | repo | No CHANGELOG; no doc of the wheel-assembly architecture (the knowledge lives only in the git log). Python 3.9 is past EOL (2025-10) — decide the support floor. |

## 4. Execution plan

Phases are ordered by leverage. **Phases 1–3 land together as one PR** — they are
coupled (version plumbing feeds the new assembly step). Do not start Phase 5 size
work until Phase 2's assembly rewrite is green.

### Phase 0 — Decisions needed from the owner (don't block; use defaults)

| Question | Default if unanswered |
|---|---|
| Author email `keinlenzo@gmail.com` — typo? | Leave as-is; flag in PR description |
| Support floor: drop Python 3.9 (EOL)? | Keep 3.9 for now |
| Add Linux aarch64? macOS x86_64? | Add aarch64 (free runners); skip Intel mac |
| Publish sdist? | No — wheels-only, documented in README |
| Keep static `.a` libs + `bin/` in the wheel? | Measure first (Phase 5), then propose |

### Phase 1 — Single source of truth for versions (F2, F7)

1. In `pyproject.toml`, bump `version = "78.3.0"` and add:
   ```toml
   [tool.icukit-pyicu]
   icu-version = "78.3"
   pyicu-version = "2.16.2"
   icu-sha256 = "<compute: curl -L <sources.tgz url> | shasum -a 256>"
   ```
2. In the workflow, replace the `env:` literals and all hardcoded `78.2.1` strings
   with values read once in a first step:
   ```bash
   python3 -c 'import tomllib; c=tomllib.load(open("pyproject.toml","rb"))' ...
   # emit PKG_VERSION / ICU_VERSION / PYICU_VERSION / ICU_SHA256 to $GITHUB_ENV
   ```
   (tomllib needs 3.11+; run this step with the setup-python interpreter only if
   ≥3.11, else `pip install tomli` — simplest: always `pip install tomli` and use
   the compat import.)
3. Add a CI guard step: fail if any `[0-9]+\.[0-9]+\.[0-9]+`-style version literal
   remains in `build.yml` (grep) — prevents regression to hardcoding.

**Acceptance:** grep for `78\.` in `build.yml` returns only comments; bumping
`pyproject.toml` alone changes every artifact name/metadata version.

### Phase 2 — Replace hand-assembly with standard tooling (F1, F3, F5, F10, F17)

Redesign of `build.yml:150-275` ("Build wheel" step):

1. **Fix `pyproject.toml` so it builds** the repo-owned part: set
   `packages = ["icukit_pyicu"]`, drop the `icu` package-dir mapping. Now
   `python -m build` produces a valid (icu-less) `icukit_pyicu` wheel with
   *correct, complete METADATA generated from pyproject* (README long-description,
   entry point, classifiers). Document in a comment that CI grafts the binary parts.
2. In CI, **merge instead of mutate**: `wheel unpack` both the setuptools-built
   `icukit_pyicu` wheel and the delocated/auditwheeled PyICU wheel; copy `icu/`,
   `icu.libs`/`pyicu.libs`/`.dylibs` payloads and the `/tmp/icu-dist`
   include/lib/bin trees into the icukit tree; then:
   - retag: `wheel tags --python-tag $PYVER --abi-tag $PYVER --platform-tag $PLAT`
   - repack: `wheel pack` (regenerates RECORD with correct hashes — delete the
     inline Python RECORD generator and all METADATA/WHEEL heredocs).
3. **Derive `$PLAT` from the delocate/auditwheel output filename** — never
   hardcode (this is also half of F4's fix).
4. **Licenses:** ship `LICENSE` (MIT) plus ICU's license file (from the extracted
   ICU source tree, `icu/LICENSE`) in the wheel dist-info; remove any leftover
   PyICU-named license artifacts from the renamed dist-info. Set PEP 639 fields in
   `pyproject.toml`: `license = "MIT AND Unicode-3.0"`,
   `license-files = ["LICENSE", "LICENSE-ICU"]` (vendor ICU's text into the repo).
5. **Gate on validation:** add a required CI step after assembly:
   `twine check dist/*.whl && check-wheel-contents dist/*.whl` (allow-list the
   known oddities like `pyicu.libs` if kept).

**Acceptance:** `python -m build` succeeds locally; final wheels pass
`twine check` + `check-wheel-contents`; `pip install` + full test suite pass in CI;
PyPI long-description renders the README; no heredoc-written metadata remains.

### Phase 3 — Correct macOS targeting & supply-chain integrity (F4, F6)

1. `export MACOSX_DEPLOYMENT_TARGET=11.0` in **both** the ICU configure step and
   the PyICU build step (macOS only). Keep `-headerpad_max_install_names`.
2. Verify in CI logs: delocate must not warn/rename; add an assertion step:
   `vtool -show-build icu/.dylibs/*.dylib | grep minos` — every lib ≤ 11.0.
3. Checksum the ICU download against `icu-sha256` from Phase 1:
   `echo "$ICU_SHA256  icu.tgz" | shasum -a 256 -c -`.
4. Pin PyICU by hash: `pip download PyICU==$PYICU_VERSION --require-hashes` with a
   one-line requirements file containing the sdist sha256 (get it from PyPI's
   "download files" page or `pip hash`).

**Acceptance:** CI fails if the tarball hash mismatches; `vtool` assertion passes;
final macOS wheel tag equals what delocate computed.

### Phase 4 — Make the shipped interface honest (F8, F12, F13)

1. `icukit_pyicu/__main__.py`: `--libs` → `-L<libdir> -licui18n -licuuc -licudata`;
   `--cflags` → `-I<includedir>`; add `--version` (read from package metadata via
   `importlib.metadata`). Keep flag names/order pkg-config-compatible.
2. Add `tests/test_icukit.py`: helpers return existing dirs (when installed from
   wheel); CLI subprocess tests for each flag.
3. CI smoke test after `pip install dist/*.whl` — compile and run a real program
   against the bundled dev files (this is the product's headline claim):
   ```bash
   cat > /tmp/t.cpp <<'EOF'
   #include <unicode/uversion.h>
   #include <cstdio>
   int main(){ UVersionInfo v; u_getVersion(v); printf("%d.%d\n", v[0], v[1]); }
   EOF
   LIB=$(python -c 'import icukit_pyicu;print(icukit_pyicu.get_lib())')
   c++ -std=c++17 $(icukit-config --cflags) /tmp/t.cpp $(icukit-config --libs) \
       -Wl,-rpath,"$LIB" -o /tmp/t && /tmp/t   # must print $ICU_VERSION major.minor
   ```
4. Fix `tests/test_icu.py::test_version`: compare `icu.ICU_VERSION` against
   `os.environ["ICU_VERSION"]` when set, else just assert it's non-empty.

**Acceptance:** smoke test passes on both OSes; `icukit-config --libs` output
links successfully; tests no longer contain a hardcoded ICU major.

### Phase 5 — Size, CI hygiene, docs (F9, F11, F15, F16, F18)

1. **Measure** wheel size before/after: report the `.a` static libs, `bin/`, and
   duplicated shared-lib contributions separately (one CI step, `du -sh` on the
   unpacked tree). Then decide (with owner, per Phase 0): likely drop `.a` files
   and keep `bin/` + one copy of shared libs; consider having `icukit_pyicu/lib`
   contain symlink-equivalents or a README pointing at the delocated copies if
   dedup is feasible (rpath constraints apply — test the Phase 4 smoke test after
   any change here).
2. Workflow hygiene: add
   ```yaml
   concurrency: {group: build-${{ github.ref }}, cancel-in-progress: true}
   ```
   and consider push-to-main building a 2-entry smoke matrix (one per OS, latest
   Python) with the full 12-entry matrix only on tags/`workflow_dispatch`/release.
3. Matrix: add `ubuntu-24.04-arm` (Linux aarch64) entries; requires the auditwheel
   plat `manylinux_2_39_aarch64` or similar — verify glibc of the arm runner image.
4. README: state platform policy explicitly (incl. why no Windows/Intel-mac/sdist);
   fix the `icukit-config` examples to match Phase 4 output; add wheel-size note.
5. Add `CHANGELOG.md` (start at 78.3.0) and `docs/BUILD.md` capturing the
   wheel-assembly architecture and the *why* behind the linker/rpath decisions
   (mine the git log: `f7cc18c`, `98a6d68`, `578effe`, `515072e`, `dc989b9`).
6. `pyproject.toml`: PEP 639 license fields (done in Phase 2), add
   `Programming Language :: Python :: 3.9`…`3.14` classifiers.

**Acceptance:** wheel size reported and reduced (or consciously kept); pushes to
main cost ≤2 jobs; docs match behavior.

## 5. Validation protocol (mandatory)

1. All local-checkable work (pyproject, CLI, tests) verified locally first.
2. Before running the full matrix, trigger `workflow_dispatch` and let **one**
   matrix entry per OS complete (temporarily comment the rest, or push to a
   branch with a reduced matrix). Confirm: build green, `twine check` green,
   smoke test green, wheel tag correct (`unzip -p dist/*.whl '*WHEEL'`).
3. macOS wheel: `vtool`/`otool -l` check for `minos 11.0`; Linux wheel:
   `auditwheel show` reports the intended manylinux tag.
4. Only then restore the full matrix.
5. **Never publish during this work**: publishing only fires on `release` events —
   do not create a GitHub release; do not add new publish triggers.
6. Version `78.3.0` gets published only by the owner cutting a release after
   review.

## 6. Explicitly out of scope

- Windows wheels (large separate effort: MSVC ICU build + delvewheel).
- Universal2 macOS wheels (single-arch arm64 is a deliberate existing choice).
- Automating upstream-version bumps (nice-to-have; a scheduled job comparing
  `tool.icukit-pyicu` pins against latest ICU/PyPI could open an issue — optional
  follow-up, not part of this plan).
