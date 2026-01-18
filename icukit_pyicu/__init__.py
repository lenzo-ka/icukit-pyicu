import os

def get_prefix():
    """Return the absolute path to the ICU installation within this package."""
    return os.path.dirname(os.path.abspath(__file__))

def get_include():
    """Return the path to the ICU include directory."""
    return os.path.join(get_prefix(), "include")

def get_lib():
    """Return the path to the ICU library directory."""
    return os.path.join(get_prefix(), "lib")

def get_bin():
    """Return the path to the ICU binaries directory."""
    return os.path.join(get_prefix(), "bin")
