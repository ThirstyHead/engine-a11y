import pytest
from engine_a11y.findings import Finding, findings_sorted, summarize, finding_to_jsonable

def test_finding_instantiation_and_dict():
    f = Finding(
        rule_id="image-alt-missing",
        sc="1.1.1",
        severity="critical",
        location="slide[1].shape[2]",
        description="Image is missing alternative text",
        evidence="<p:pic>",
        fixable=True,
        fix="Add alternative text",
        why_unfixable=None,
        manual_steps=["Open format picture pane", "Add alt text description"],
        excluded=False,
    )
    assert f.blocking is True
    d = f.to_dict()
    assert d["rule_id"] == "image-alt-missing"
    assert d["manual_steps"] == ["Open format picture pane", "Add alt text description"]
    assert d["excluded"] is False
    assert finding_to_jsonable(f) == d

def test_findings_sorting_and_excluded():
    f_minor = Finding("r1", "1.1.1", "minor", "loc A", "desc")
    f_crit = Finding("r2", "1.1.1", "critical", "loc B", "desc")
    f_ser = Finding("r3", "1.1.1", "serious", "loc C", "desc")
    # Excluded critical finding should sort after active findings
    f_ex_crit = Finding("r4", "1.1.1", "critical", "loc D", "desc", excluded=True)

    sorted_f = findings_sorted([f_ex_crit, f_minor, f_crit, f_ser])
    assert [f.rule_id for f in sorted_f] == ["r2", "r3", "r1", "r4"]

def test_summarize_with_excluded_bucket():
    # Active findings
    f1 = Finding("image-alt-missing", "1.1.1", "critical", "loc1", "desc1")
    f2 = Finding("heading-skipped", "1.3.1", "serious", "loc2", "desc2")
    # Excluded findings (e.g. contrast unchecked by user in what-if test)
    f3 = Finding("contrast-low", "1.4.3", "serious", "loc3", "desc3", excluded=True)
    f4 = Finding("contrast-low", "1.4.3", "moderate", "loc4", "desc4", excluded=True)

    summary = summarize([f1, f2, f3, f4])

    # Overall totals
    assert summary["total"] == 4
    assert summary["active_total"] == 2
    assert summary["excluded_total"] == 2

    # Blocking calculations: only active critical/serious count toward failure
    assert summary["blocking"] == 2
    assert summary["active_blocking"] == 2
    assert summary["excluded_blocking"] == 1
    assert summary["pass"] is False

    # Excluded bucket details
    assert summary["excluded"]["total"] == 2
    assert summary["excluded"]["blocking"] == 1
    assert summary["excluded"]["by_severity"]["serious"] == 1
    assert summary["excluded"]["by_severity"]["moderate"] == 1

def test_summarize_clean_with_only_excluded_failures():
    # What-if scenario: all non-contrast barriers fixed, contrast excluded
    f_contrast = Finding("contrast-low", "1.4.3", "critical", "loc1", "desc", excluded=True)
    summary = summarize([f_contrast])

    assert summary["total"] == 1
    assert summary["active_total"] == 0
    assert summary["active_blocking"] == 0
    assert summary["excluded_total"] == 1
    assert summary["excluded_blocking"] == 1
    # Compliance pass is True for active criteria, with note that excluded items exist
    assert summary["pass"] is True
    assert summary["has_excluded_barriers"] is True
