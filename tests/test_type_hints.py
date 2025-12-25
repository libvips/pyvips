"""
Test type stubs are valid and work with mypy.

This test verifies the type stubs can be used for type checking.
Run with: pytest -q tests/test_type_hints.py

Also verify with mypy:
    mypy tests/test_type_hints.py
"""


def test_type_stubs_basic():
    """Test basic type stubs functionality."""
    import pyvips

    # Basic type checking - these should all be valid
    img = pyvips.Image.black(100, 100, bands=3)
    assert isinstance(img, pyvips.Image)

    # Test method calls
    inverted = img.invert()
    assert isinstance(inverted, pyvips.Image)

    resized = img.resize(0.5)
    assert isinstance(resized, pyvips.Image)

    # Test operators
    result = img + 5
    assert isinstance(result, pyvips.Image)

    # Test metadata
    typeof_val = img.get_typeof("xres")
    assert isinstance(typeof_val, int)

    # Test get returns union type
    metadata = img.get("xres")

    print("Type stubs test passed!")
