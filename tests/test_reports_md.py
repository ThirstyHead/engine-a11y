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


def test_render_md_includes_scorecard_and_encouragement():
    before = {
        "file": "test.docx",
        "summary": {"total": 2, "blocking": 2, "pass": False},
        "findings": [
            {
                "rule_id": "title-missing",
                "sc": "2.4.2",
                "severity": "serious",
                "location": "doc/props",
                "description": "Document title is missing",
                "fixable": True,
                "fix": "Set title metadata to filename",
            },
            {
                "rule_id": "image-alt-missing",
                "sc": "1.1.1",
                "severity": "critical",
                "location": "img[0]",
                "description": "Image is missing alt text",
                "fixable": False,
                "manual_steps": ["Right-click image", "Select View Alt Text", "Add meaningful description"],
            },
        ],
    }
    after = {
        "file": "test.fixed.docx",
        "summary": {"total": 1, "blocking": 1, "pass": False},
        "findings": [
            {
                "rule_id": "image-alt-missing",
                "sc": "1.1.1",
                "severity": "critical",
                "location": "img[0]",
                "description": "Image is missing alt text",
                "fixable": False,
                "manual_steps": ["Right-click image", "Select View Alt Text", "Add meaningful description"],
            }
        ],
    }
    report = render_md(before, after_result=after)
    # Scorecard assertions
    assert "Document Remediation Scorecard" in report
    assert "Original Barriers Detected" in report
    assert "Automatically Fixed & Incorporated" in report
    assert "Remaining Human Actions" in report
    assert "50.0%" in report or "50%" in report

    # Dedicated Fixes Incorporated section
    assert "## Fixes Incorporated into Remediated Document" in report
    assert "✅" in report
    assert "doc/props" in report
    assert "2.4.2" in report

    # Action Checklist for human author
    assert "## Action Checklist: Human-in-the-Loop Next Steps" in report
    assert "- [ ]" in report
    assert "Why Automated Software Cannot Fix This:" in report
    assert "Step-by-Step Instructions:" in report

    # Badges in detailed findings
    assert "[RESOLVED BY AUTO-REMEDIATION]" in report
    assert "[ACTION REQUIRED - HUMAN IN THE LOOP]" in report


def test_render_md_all_clean_no_actions():
    clean_audit = {
        "file": "perfect.docx",
        "summary": {"total": 0, "blocking": 0, "pass": True},
        "findings": [],
    }
    report = render_md(clean_audit)
    assert "Outstanding!" in report
    assert "COMPLIANT" in report
    assert "No accessibility barriers detected" in report
