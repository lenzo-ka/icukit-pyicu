# icukit-pyicu

**Bundled ICU and PyICU for pip**

## Install

```bash
pip install icukit-pyicu
```

No Homebrew. No apt-get. Just pip.

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

- macOS: ARM64, x86_64
- Linux: x86_64
- Python: 3.9+

## License

MIT (see `LICENSE` for details).

This project bundles binary distributions of **ICU** (ICU License) and **PyICU** (MIT License).

It also provides a Python module `icukit_pyicu` with helpers and the standard `icu` module.
