"""Tests for social model tone, encouraging progress banners, and human-in-the-loop explanations."""
import pytest
from engine_a11y.reports.tone import (
    assert_social_model_language,
    get_encouraging_progress_banner,
    HUMAN_IN_THE_LOOP_EXPLANATIONS,
)


def test_encouraging_progress_banner_tone():
    banner = get_encouraging_progress_banner(resolved=4, remaining=1, total=5)
    assert "80.0%" in banner or "80%" in banner
    assert "progress" in banner.lower() or "great" in banner.lower()
    # Ensure no medical model language in banner
    assert_social_model_language(banner)


def test_encouraging_progress_banner_all_clean():
    banner = get_encouraging_progress_banner(resolved=0, remaining=0, total=0)
    assert "meets all" in banner.lower() or "outstanding" in banner.lower()
    assert_social_model_language(banner)


def test_encouraging_progress_banner_all_resolved():
    banner = get_encouraging_progress_banner(resolved=3, remaining=0, total=3)
    assert "all 3" in banner.lower() or "fantastic" in banner.lower()
    assert_social_model_language(banner)


def test_human_in_the_loop_explanations_exist():
    assert "image-alt-missing" in HUMAN_IN_THE_LOOP_EXPLANATIONS
    explanation = HUMAN_IN_THE_LOOP_EXPLANATIONS["image-alt-missing"]
    assert "author" in explanation.lower()
    assert_social_model_language(explanation)


def test_assert_social_model_language_raises_on_banned():
    with pytest.raises(ValueError, match="Prohibited language"):
        assert_social_model_language("This file is broken for handicapped people.")
