import pytest
from engine_a11y.reports.md import render_md
from engine_a11y.profile import get_docx_profile

def test_render_md_basic():
    result = {
        "file": "test.docx",
        "sha256": "abcdef123456",
        "tool": "engine-a11y/0.1.0",
        "summary": {
            "total": 1,
            "active_total": 1,
            "excluded_total": 0,
            "blocking": 1,
            "active_blocking": 1,
            "excluded_blocking": 0,
            "pass": False,
            "has_excluded_barriers": False,
        },
        "findings": [
            {
                "rule_id": "image-alt-missing",
                "sc": "1.1.1",
                "severity": "critical",
                "location": "p[1]",
                "description": "Image is missing alt text",
                "fix": "Add alt text",
                "evidence": "<pic>",
                "excluded": False,
            }
        ]
    }
    report = render_md(result, profile=get_docx_profile())
    assert "# Accessibility Audit Report: test.docx" in report
    assert "WCAG Conformance & Coverage Matrix" in report
    assert "1.1.1" in report
    assert "[FAIL]" in report
    assert "1.4.3" in report  # Full matrix contains all SCs!
    assert "Executive Summary" in report

def test_render_md_what_if_excluded():
    result = {
        "file": "brand_test.docx",
        "sha256": "123456abcdef",
        "tool": "engine-a11y/0.1.0",
        "summary": {
            "total": 1,
            "active_total": 0,
            "excluded_total": 1,
            "blocking": 0,
            "active_blocking": 0,
            "excluded_blocking": 1,
            "pass": True,
            "has_excluded_barriers": True,
        },
        "findings": [
            {
                "rule_id": "contrast-low",
                "sc": "1.4.3",
                "severity": "serious",
                "location": "run[3]",
                "description": "Contrast ratio 2.1:1 below threshold",
                "fix": "Adjust color",
                "evidence": "fg=#777777 bg=#ffffff",
                "excluded": True,
            }
        ]
    }
    report = render_md(result, profile=get_docx_profile(), excluded_sc={"1.4.3"})
    assert "What-If Analysis Active" in report
    assert "[EXCLUDED FROM SUMMARY]" in report
    assert "COMPLIANT" in report or "PASS" in report
    assert "1.4.3" in report
