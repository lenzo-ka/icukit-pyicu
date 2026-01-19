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
icukit-config --prefix
icukit-config --cflags
icukit-config --libs
```

## Platforms

- macOS: ARM64 (Apple Silicon)
- Linux: x86_64
- Python: 3.9+

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

MIT (see `LICENSE` for details).

This project bundles binary distributions of **ICU** (ICU License) and **PyICU** (MIT License).

It also provides a Python module `icukit_pyicu` with helpers and the standard `icu` module.
