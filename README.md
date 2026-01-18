# icukit-icu

**ICU 75.1 + PyICU 2.16 for pip**

## Install

```bash
pip install icukit-icu
```

No Homebrew. No apt-get. Just pip.

## Usage

```python
import icu

t = icu.Transliterator.createInstance("Latin-Cyrillic")
print(t.transliterate("Hello"))  # Хелло
```

## Platforms

- macOS: ARM64, x86_64
- Linux: x86_64
- Python: 3.9 - 3.12

## License

ICU License
