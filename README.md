# icukit-icu

**ICU for pip** - International Components for Unicode, packaged for Python.

## Install

```bash
pip install icukit-icu
```

## What's included

- **PyICU** - Python bindings (`import icu`)
- **ICU libraries** - libicuuc, libicui18n, libicudata (bundled)

No Homebrew. No apt-get. Just pip.

## Usage

```python
import icu

t = icu.Transliterator.createInstance("Latin-Cyrillic")
print(t.transliterate("Hello"))  # Хелло
```

## Versions

| icukit-icu | ICU | PyICU |
|------------|-----|-------|
| 75.1.x     | 75.1 | 2.16 |

PyICU 2.16 requires ICU 75+ to be built with C++17 (handled automatically in our wheels).

## Platforms

- macOS: ARM64, x86_64
- Linux: x86_64 (manylinux_2_28)
- Python: 3.9 - 3.12

## License

ICU License (BSD-style)
