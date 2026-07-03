# icukit-pyicu

[ICU](https://icu.unicode.org/) is a marvel of engineering, built from years of cooperation across major platforms and the Unicode Consortium, and [PyICU](https://gitlab.pyicu.org/main/pyicu) exposes much of the functionality in Python. This package includes the libraries and headers from ICU, and provides the PyICU package using it.

## Batteries Included ICU and PyICU

PyICU can be hard to install on macOS and Linux because it requires ICU libraries to be installed first. This package bundles source-built ICU with PyICU, so everything installs in one go.

## Install

```bash
pip install icukit-pyicu
```

## Usage

```python
import icu

t = icu.Transliterator.createInstance("Latin-Cyrillic")
print(t.transliterate("Hello"))  # Хелло
```

### Development and Linkage

`icukit-pyicu` also bundles the full ICU headers and libraries for use in other projects:

```python
import icukit_pyicu

print(icukit_pyicu.get_include())  # Path to ICU headers
print(icukit_pyicu.get_lib())      # Path to ICU libraries
print(icukit_pyicu.get_bin())      # Path to ICU binaries
```

It also provides a CLI tool similar to `pkg-config`:

```bash
icukit-config --version   # package version, e.g. 78.3.0
icukit-config --prefix    # install prefix
icukit-config --cflags    # -I<includedir>
icukit-config --libs      # -L<libdir> -licui18n -licuuc -licudata
```

For example, to compile and link a C++ program against the bundled ICU:

```bash
c++ -std=c++17 $(icukit-config --cflags) prog.cpp $(icukit-config --libs) \
    -Wl,-rpath,"$(python -c 'import icukit_pyicu;print(icukit_pyicu.get_lib())')"
```

## Platforms

Wheels are published for:

- macOS: ARM64 (Apple Silicon)
- Linux: x86_64 and aarch64 (manylinux)
- Python: 3.9–3.14

Only these binary wheels are published; there is no source distribution
(building requires compiling ICU from source, which the CI pipeline handles).
Intel macOS and Windows are not currently targeted. The wheels bundle both the
ICU runtime libraries and the full ICU dev headers/libraries, so they are large
(tens of MB) by design.

## Note on PyICU

This package provides its own `icu` module. If you have `PyICU` installed separately, they will conflict. Either uninstall PyICU first, or use a virtual environment:

```bash
pip uninstall PyICU
pip install icukit-pyicu
```

Or with a venv:

```bash
python -m venv myenv
source myenv/bin/activate
pip install icukit-pyicu
```

## License

The `icukit_pyicu` helper code is MIT (see `LICENSE`).

The published wheels bundle binary distributions of **ICU** (Unicode-3.0
license, see `LICENSE-ICU`) and **PyICU** (MIT). Accordingly the wheel metadata
declares the SPDX expression `MIT AND Unicode-3.0`, and both license files are
included in the distribution.
