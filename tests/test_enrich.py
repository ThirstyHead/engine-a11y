import pytest
from engine_a11y.enrich import (
    Cache,
    build_enrichment,
    get_criterion_text,
    load_cache_json,
    parse_criterion,
)

def test_load_cache_json():
    data = load_cache_json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "1.1.1" in data
    assert "1.4.3" in data

def test_get_criterion_text():
    text = get_criterion_text("1.1.1")
    assert text is not None
    assert "Non-text Content" in text

def test_parse_criterion():
    raw_md = """# 1.1.1 Non-text Content
**Level:** A
**Principle:** 1. Perceivable
**Guideline:** 1.1 Text Alternatives

## In Brief
All non-text content that is presented to the user has a text alternative.

## Description
Short description here.

## Intent
The intent of this Success Criterion is to make information accessible.
"""
    parsed = parse_criterion(raw_md)
    assert parsed["num"] == "1.1.1"
    assert parsed["handle"] == "Non-text Content"
    assert parsed["level"] == "A"
    assert parsed["principle"] == "1. Perceivable"
    assert parsed["in_brief"].startswith("All non-text content")
    assert parsed["intent"].startswith("The intent of this Success Criterion")

def test_build_enrichment():
    result = {
        "findings": [
            {"sc": "1.1.1", "rule_id": "r1"},
            {"sc": "1.4.3", "rule_id": "r2"},
        ]
    }
    enrichment, source = build_enrichment(result)
    assert "1.1.1" in enrichment
    assert "1.4.3" in enrichment
    assert enrichment["1.1.1"]["num"] == "1.1.1"
    assert "sc_cache.json" in source
