import pytest
from engine_a11y.profile import (
    DocumentProfile,
    SCStatus,
    evaluate_sc_matrix,
    get_complete_wcag_catalog,
    get_docx_profile,
    get_pptx_profile,
    get_xlsx_profile,
    get_pdf_profile,
)
from engine_a11y.findings import Finding

def test_complete_wcag_catalog_coverage():
    catalog = get_complete_wcag_catalog()
    assert len(catalog) >= 50
    assert "1.1.1" in catalog
    assert "1.4.3" in catalog
    assert "2.4.2" in catalog
    assert "4.1.2" in catalog

def test_evaluate_sc_matrix_with_custom_profile():
    profile = DocumentProfile(
        name="Word Document",
        doc_type="Document",
        automated_sc={"1.1.1": "Checks drawing alt text", "2.4.2": "Checks core.xml title"},
        human_in_the_loop_sc={"1.3.2": "Verify reading order matches logical flow"},
        not_applicable_sc={"1.4.2": "Audio controls not applicable to static Word documents"},
        unchecked_sc={"1.4.10": "Reflow requires dynamic viewport rendering"},
    )
    findings = [
        Finding(rule_id="image-alt-missing", sc="1.1.1", severity="critical", location="P1", description="No alt")
    ]
    matrix = evaluate_sc_matrix(findings=findings, profile=profile)

    # 1.1.1 was checked and had a finding -> FAIL
    assert matrix["1.1.1"]["status"] == SCStatus.FAIL
    assert len(matrix["1.1.1"]["findings"]) == 1

    # 2.4.2 was checked and had no findings -> PASS
    assert matrix["2.4.2"]["status"] == SCStatus.PASS

    # 1.3.2 requires human review
    assert matrix["1.3.2"]["status"] == SCStatus.MANUAL_REVIEW
    assert "Verify reading order" in matrix["1.3.2"]["annotation"]

    # 1.4.2 is not applicable
    assert matrix["1.4.2"]["status"] == SCStatus.NOT_APPLICABLE
    assert "Audio controls not applicable" in matrix["1.4.2"]["annotation"]

    # 1.4.10 is unchecked with rationale
    assert matrix["1.4.10"]["status"] == SCStatus.UNCHECKED
    assert "Reflow requires dynamic" in matrix["1.4.10"]["annotation"]

    # Other SC not explicitly mapped default to UNCHECKED
    assert matrix["2.1.1"]["status"] == SCStatus.UNCHECKED

def test_evaluate_sc_matrix_with_excluded_sc():
    profile = get_docx_profile()
    findings = [
        Finding(rule_id="contrast-low", sc="1.4.3", severity="serious", location="P1", description="Low contrast", excluded=True)
    ]
    # 1.4.3 was excluded by user in what-if test
    matrix = evaluate_sc_matrix(findings=findings, profile=profile, excluded_sc={"1.4.3"})
    assert matrix["1.4.3"]["is_excluded"] is True
    assert matrix["1.4.3"]["status"] == SCStatus.FAIL
    assert "[EXCLUDED FROM SUMMARY]" in matrix["1.4.3"]["annotation"]

def test_format_profiles():
    docx_p = get_docx_profile()
    assert docx_p.doc_type == "Document"
    assert "1.1.1" in docx_p.automated_sc
    assert "1.4.2" in docx_p.not_applicable_sc

    pptx_p = get_pptx_profile()
    assert pptx_p.doc_type == "Presentation"
    assert "1.3.2" in pptx_p.automated_sc

    xlsx_p = get_xlsx_profile()
    assert xlsx_p.doc_type == "Workbook"

    pdf_p = get_pdf_profile()
    assert pdf_p.doc_type == "PDF"
    assert "4.1.2" in pdf_p.automated_sc
