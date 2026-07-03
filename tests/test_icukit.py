"""Tests for the icukit_pyicu helper package and the icukit-config CLI.

These exercise the dev-linkage surface (headers/libs/bin discovery and the
pkg-config-style CLI). The path-existence checks only assert real directories
when the package was installed from a built wheel (where the ICU dev tree is
present); in a plain source checkout those directories do not exist, so the
checks are skipped.
"""

import os
import subprocess
import sys

import icukit_pyicu
from icukit_pyicu.__main__ import ICU_LIBS, build_output, main


class _Args:
    def __init__(self, **kw):
        for name in ("version", "prefix", "cflags", "libs", "bindir"):
            setattr(self, name, kw.get(name, False))


def _bundled():
    """True when the ICU dev tree is present (installed from a built wheel)."""
    return os.path.isdir(icukit_pyicu.get_include())


def test_helpers_return_paths_under_prefix():
    prefix = icukit_pyicu.get_prefix()
    assert icukit_pyicu.get_include() == os.path.join(prefix, "include")
    assert icukit_pyicu.get_lib() == os.path.join(prefix, "lib")
    assert icukit_pyicu.get_bin() == os.path.join(prefix, "bin")


def test_cflags_output():
    out = build_output(_Args(cflags=True))
    assert out == [f"-I{icukit_pyicu.get_include()}"]


def test_libs_output_includes_link_flags():
    out = build_output(_Args(libs=True))
    assert out[0] == f"-L{icukit_pyicu.get_lib()}"
    assert out[1:] == [f"-l{name}" for name in ICU_LIBS]
    assert "-licui18n" in out and "-licuuc" in out and "-licudata" in out


def test_version_output_nonempty():
    out = build_output(_Args(version=True))
    assert out and out[0]


def test_main_no_args_prints_help_and_returns_1():
    assert main([]) == 1


def test_cli_subprocess_libs():
    """Run the installed console script end to end."""
    result = subprocess.run(
        [sys.executable, "-m", "icukit_pyicu", "--libs"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "-licui18n" in result.stdout


def test_bundled_dev_tree_exists_when_installed():
    """When installed from a wheel, the advertised dev directories must exist."""
    if not _bundled():
        import pytest
        pytest.skip("running from source checkout; ICU dev tree not present")
    assert os.path.isdir(icukit_pyicu.get_include())
    assert os.path.isdir(icukit_pyicu.get_lib())
    assert os.path.isdir(icukit_pyicu.get_bin())
    # A core header consumers rely on.
    assert os.path.isfile(
        os.path.join(icukit_pyicu.get_include(), "unicode", "uversion.h")
    )
