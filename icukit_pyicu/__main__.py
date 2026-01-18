import sys
import argparse
from icukit_pyicu import get_prefix, get_include, get_lib, get_bin

def main():
    parser = argparse.ArgumentParser(description="ICU configuration tool for icukit-pyicu")
    parser.add_argument("--prefix", action="store_true", help="Print the ICU prefix path")
    parser.add_argument("--cflags", "--include", action="store_true", help="Print the include path")
    parser.add_argument("--libs", "--lib", action="store_true", help="Print the library path")
    parser.add_argument("--bindir", "--bin", action="store_true", help="Print the binary path")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    results = []
    if args.prefix:
        results.append(get_prefix())
    if args.cflags:
        results.append(f"-I{get_include()}")
    if args.libs:
        results.append(f"-L{get_lib()}")
    if args.bindir:
        results.append(get_bin())

    if results:
        print(" ".join(results))

if __name__ == "__main__":
    main()
