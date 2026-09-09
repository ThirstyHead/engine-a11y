import pytest
from pathlib import Path
from engine_a11y.reports.html import render_html
from engine_a11y.reports.pdf import render_pdf

SAMPLE_MD = """# Accessibility Audit Report: presentation.pptx

- **Document Evaluated:** `presentation.pptx`
- **Audit Standard:** [WCAG 2.1 & 2.2 Levels A & AA](https://www.w3.org)
- **Compliance Status:** **NON-COMPLIANT**

## Executive Summary

> **Assessment:** This document contains accessibility barriers that need attention.

## WCAG Conformance & Coverage Matrix

| Success Criterion | Title | Level | Principle | Status | Evaluation Details |
|---|---|---|---|---|---|
| [1.1.1](https://w3.org) | Non-text Content | A | Perceivable | [FAIL] | Missing alt text on slide 1 |
| [1.4.3](https://w3.org) | Contrast (Minimum) | AA | Perceivable | [PASS] | Contrast checks passed |

## 1. Perceivable

### 1. [CRITICAL] Image missing alt text

- **Success Criterion:** WCAG SC 1.1.1
- **Location:** `Slide 1 Shape 2`
"""

def test_render_html():
    html_out = render_html(SAMPLE_MD, theme="light")
    assert "<!doctype html>" in html_out
    assert '<html lang="en">' in html_out
    assert 'class="summary-banner"' in html_out
    assert 'class="toc"' in html_out
    assert "WCAG Conformance &amp; Coverage Matrix" in html_out

def test_render_pdf(tmp_path):
    html_doc = render_html(SAMPLE_MD, theme="light")
    pdf_out = tmp_path / "test_report.pdf"
    res_path = render_pdf(html_doc, out_path=pdf_out, title="Test Report")
    assert res_path.exists()
    assert res_path.stat().st_size > 1000
