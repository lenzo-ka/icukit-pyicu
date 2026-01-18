# icukit-icu

**ICU 75.1 for pip** - International Components for Unicode, packaged for Python.

## Install

```bash
pip install icukit-icu
```

## What's included

Everything from ICU 75.1:

- **Libraries**: libicuuc, libicui18n, libicudata
- **Headers**: Full ICU C/C++ headers
- **Data**: ICU data files
- **PyICU**: Python bindings (`import icu`)

## Usage

```python
import icu

# You have full PyICU
t = icu.Transliterator.createInstance("Latin-Cyrillic")
print(t.transliterate("Hello"))
```

## Platforms

- macOS: ARM64, x86_64
- Linux: x86_64 (manylinux_2_28)
- Python: 3.9 - 3.12

## Version

ICU 75.1 (release-75-1)

## License

ICU License
