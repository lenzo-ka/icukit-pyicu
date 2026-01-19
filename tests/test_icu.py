"""Basic tests for icukit-pyicu to verify ICU functionality."""

import icu


def test_version():
    """Verify ICU and PyICU versions."""
    assert icu.ICU_VERSION.startswith("75.")
    assert icu.PYICU_VERSION == "2.16"


def test_locale():
    """Test locale creation and properties."""
    locale = icu.Locale("en_US")
    assert locale.getLanguage() == "en"
    assert locale.getCountry() == "US"
    
    locale_de = icu.Locale("de_DE")
    assert locale_de.getLanguage() == "de"


def test_normalization():
    """Test Unicode normalization."""
    nfkc = icu.Normalizer2.getNFKCInstance()
    # Ligature fi -> fi
    assert nfkc.normalize("\ufb01") == "fi"
    # Full-width A -> A
    assert nfkc.normalize("\uff21") == "A"


def test_collation():
    """Test collation (locale-aware sorting)."""
    collator = icu.Collator.createInstance(icu.Locale("en_US"))
    # Basic comparison
    assert collator.compare("apple", "banana") < 0
    assert collator.compare("zebra", "apple") > 0
    assert collator.compare("test", "test") == 0


def test_transliteration():
    """Test transliteration between scripts."""
    # Latin to Cyrillic
    t = icu.Transliterator.createInstance("Latin-Cyrillic")
    assert t.transliterate("hello") == "хелло"
    
    # Any to Latin (useful for romanization)
    t2 = icu.Transliterator.createInstance("Any-Latin")
    assert t2.transliterate("日本語") is not None  # Should produce romanized form


def test_break_iterator():
    """Test word boundary detection."""
    text = "Hello, world! How are you?"
    bi = icu.BreakIterator.createWordInstance(icu.Locale.getUS())
    bi.setText(text)
    
    boundaries = []
    pos = bi.nextBoundary()
    while pos != icu.BreakIterator.DONE:
        boundaries.append(pos)
        pos = bi.nextBoundary()
    
    # Should find multiple word boundaries
    assert len(boundaries) > 3


def test_calendar():
    """Test calendar creation (verifies ICU data is loaded)."""
    cal = icu.Calendar.createInstance(icu.Locale("en_US"))
    assert cal is not None
    
    # Test Japanese calendar (requires ICU data)
    cal_jp = icu.Calendar.createInstance(icu.Locale("ja_JP"))
    assert cal_jp is not None


def test_number_format():
    """Test number formatting."""
    # German uses . for thousands separator
    nf = icu.NumberFormat.createInstance(icu.Locale("de_DE"))
    formatted = nf.format(1234567)
    assert "." in formatted or "," in formatted  # Locale-specific separator


def test_charset_detection():
    """Test character set detection."""
    detector = icu.CharsetDetector()
    detector.setText(b"Hello, world!")
    match = detector.detect()
    assert match is not None


if __name__ == "__main__":
    # Run tests manually
    test_version()
    test_locale()
    test_normalization()
    test_collation()
    test_transliteration()
    test_break_iterator()
    test_calendar()
    test_number_format()
    test_charset_detection()
    print("All tests passed!")
