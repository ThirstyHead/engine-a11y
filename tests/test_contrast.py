import pytest
from engine_a11y.contrast import (
    adjust_color_for_contrast,
    contrast_ratio,
    hex_to_rgb,
    is_contrast_acceptable,
    relative_luminance,
)

def test_hex_to_rgb():
    assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("000000") == (0, 0, 0)
    assert hex_to_rgb("#FFF") == (255, 255, 255)
    assert hex_to_rgb("invalid") is None

def test_contrast_ratio_black_white():
    ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
    assert pytest.approx(ratio, 0.1) == 21.0

def test_contrast_ratio_same_color():
    ratio = contrast_ratio((128, 128, 128), (128, 128, 128))
    assert pytest.approx(ratio, 0.01) == 1.0

def test_is_contrast_acceptable():
    assert is_contrast_acceptable("000000", "FFFFFF") is True
    assert is_contrast_acceptable("777777", "FFFFFF") is False
    assert is_contrast_acceptable("777777", "FFFFFF", is_large=True) is True

def test_adjust_color_for_contrast():
    adjusted = adjust_color_for_contrast("777777", "FFFFFF", target_ratio=4.5)
    assert is_contrast_acceptable(adjusted, "FFFFFF") is True

    adjusted_light = adjust_color_for_contrast("333333", "000000", target_ratio=4.5)
    assert is_contrast_acceptable(adjusted_light, "000000") is True
