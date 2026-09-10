"""Tests for finding-level progress statistics and diffs."""
from engine_a11y.findings import Finding
from engine_a11y.reports.stats import diff_findings


def test_diff_findings_partitions_resolved_and_remaining():
    f1 = Finding(
        rule_id="title-missing",
        sc="2.4.2",
        severity="serious",
        location="doc/props",
        description="No title",
        fixable=True,
    )
    f2 = Finding(
        rule_id="image-alt-missing",
        sc="1.1.1",
        severity="critical",
        location="img[0]",
        description="Missing alt",
        fixable=False,
        why_unfixable="Requires author description",
    )

    before_findings = [f1, f2]
    # In after audit, title was added by remediation, but image alt remains
    after_findings = [f2]

    diff = diff_findings(before_findings, after_findings)
    assert len(diff["resolved"]) == 1
    assert diff["resolved"][0].rule_id == "title-missing"
    assert len(diff["remaining"]) == 1
    assert diff["remaining"][0].rule_id == "image-alt-missing"
    assert diff["resolved_count"] == 1
    assert diff["remaining_count"] == 1


def test_diff_findings_audit_only_mode():
    f1 = Finding(
        rule_id="title-missing",
        sc="2.4.2",
        severity="serious",
        location="doc/props",
        description="No title",
        fixable=True,
    )
    f2 = Finding(
        rule_id="image-alt-missing",
        sc="1.1.1",
        severity="critical",
        location="img[0]",
        description="Missing alt",
        fixable=False,
    )
    diff = diff_findings([f1, f2], None)
    assert diff["mode"] == "audit_only"
    assert diff["resolved_count"] == 0
    assert len(diff["auto_fixable"]) == 1
    assert len(diff["manual_only"]) == 1
