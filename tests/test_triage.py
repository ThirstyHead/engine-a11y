import pytest
from engine_a11y.triage import TriageItem, TriageSession

def test_triage_session_build_items():
    findings = [
        {"rule_id": "title-missing", "location": "doc", "message": "No title"},
        {"rule_id": "language-missing", "location": "doc", "message": "No language", "evidence": "und"},
        {"rule_id": "image-alt-missing", "location": "slide[1].shape[2]", "message": "Image alt missing"},
        {"rule_id": "contrast-low", "location": "slide[1].shape[3]", "message": "Contrast low"},
    ]
    session = TriageSession(findings)
    items = session.items
    assert len(items) == 3  # contrast-low is purely algorithmic, not interactive author intent
    assert items[0].rule_id == "title-missing"
    assert items[1].rule_id == "language-missing"
    assert items[2].rule_id == "image-alt-missing"

def test_triage_session_resolution():
    findings = [
        {"rule_id": "title-missing", "location": "doc", "message": "No title"},
        {"rule_id": "image-alt-missing", "location": "img1", "message": "No alt"},
    ]
    session = TriageSession(findings)
    assert len(session.get_pending_items()) == 2

    session.resolve_item(0, "Quarterly Financial Report")
    assert len(session.get_pending_items()) == 1

    session.resolve_item(1, "Bar chart showing Q3 revenue growth")
    assert len(session.get_pending_items()) == 0

    overrides = session.to_context_overrides()
    assert overrides["title"] == "Quarterly Financial Report"
    assert overrides["alt_map"]["img1"] == "Bar chart showing Q3 revenue growth"
