import sys
import argparse

from icukit_pyicu import get_prefix, get_include, get_lib, get_bin

# The core ICU shared libraries a consumer links against, in dependency order
# (i18n -> uc -> data), matching what `pkg-config --libs icu-i18n` emits.
ICU_LIBS = ["icui18n", "icuuc", "icudata"]


def _version():
    from importlib.metadata import version, PackageNotFoundError
    try:
        return version("icukit-pyicu")
    except PackageNotFoundError:
        return "unknown"


def build_output(args):
    """Return the list of output tokens for the given parsed args."""
    results = []
    if args.version:
        results.append(_version())
    if args.prefix:
        results.append(get_prefix())
    if args.cflags:
        results.append(f"-I{get_include()}")
    if args.libs:
        results.append(f"-L{get_lib()}")
        results.extend(f"-l{name}" for name in ICU_LIBS)
    if args.bindir:
        results.append(get_bin())
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ICU configuration tool for icukit-pyicu (pkg-config style)"
    )
    parser.add_argument("--version", action="store_true",
                        help="Print the icukit-pyicu package version")
    parser.add_argument("--prefix", action="store_true",
                        help="Print the ICU prefix path")
    parser.add_argument("--cflags", "--include", action="store_true",
                        help="Print compiler include flags (-I...)")
    parser.add_argument("--libs", "--lib", action="store_true",
                        help="Print linker flags (-L... -licui18n -licuuc -licudata)")
    parser.add_argument("--bindir", "--bin", action="store_true",
                        help="Print the ICU binary path")

    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        parser.print_help()
        return 1

    args = parser.parse_args(argv)
    results = build_output(args)
    if results:
        print(" ".join(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
