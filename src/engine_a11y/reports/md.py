"""Markdown report generator with full WCAG Conformance Matrix and What-If Excluded Bucket."""
from typing import Any, Dict, List, Optional, Set
from .. import __version__
from ..findings import Finding
from ..profile import DocumentProfile, evaluate_sc_matrix
from .meta import POUR_INTROS, PRINCIPLES, SC_META, W3C_QUICKREF
from .stats import compute_progress_stats
from .tone import RULE_BARRIER_EXPLANATIONS, WHO_MAP, WORD_ASSISTANT_NOTES, assert_social_model_language


def render_md(
    result: Dict[str, Any],
    after_result: Optional[Dict[str, Any]] = None,
    source_path: Optional[str] = None,
    profile: Optional[DocumentProfile] = None,
    excluded_sc: Optional[Set[str]] = None,
) -> str:
    src = source_path or result.get("file", "document")
    summary = result.get("summary", {})
    raw_findings = result.get("findings", [])
    excluded = set(excluded_sc or [])

    # Convert finding dicts to Finding instances if needed
    finding_objs: List[Finding] = []
    for f in raw_findings:
        if isinstance(f, Finding):
            finding_objs.append(f)
        else:
            finding_objs.append(
                Finding(
                    rule_id=f.get("rule_id", "custom-rule"),
                    sc=f.get("sc", "1.1.1"),
                    severity=f.get("severity", "moderate"),
                    location=f.get("location", ""),
                    description=f.get("description", ""),
                    evidence=f.get("evidence", ""),
                    fixable=f.get("fixable", False),
                    fix=f.get("fix", ""),
                    why_unfixable=f.get("why_unfixable"),
                    manual_steps=f.get("manual_steps", []),
                    excluded=f.get("excluded", False) or f.get("sc") in excluded,
                )
            )

    after_summary = after_result.get("summary") if after_result else None
    stats = compute_progress_stats(summary, after_summary)

    lines: List[str] = []
    lines.append(f"# Accessibility Audit Report: {src}")
    lines.append("")
    lines.append(f"- **Document Evaluated:** `{src}`")
    lines.append(f"- **Original File SHA-256:** `{result.get('sha256', 'n/a')}`")
    lines.append("- **Integrity Verification:** Immutable (original document is strictly read-only and never modified in place)")
    lines.append(f"- **Audit Standard:** [WCAG 2.1 & 2.2 Levels A & AA]({W3C_QUICKREF})")
    lines.append(f"- **Evaluated At:** {result.get('audited_at', 'n/a')}")
    lines.append(f"- **Audit Tool:** `{result.get('tool', f'engine-a11y/{__version__}')}`")

    # Compliance status
    is_compliant = summary.get("pass", False)
    status_label = "COMPLIANT (Passes WCAG AA Requirements)" if is_compliant else "NON-COMPLIANT (Blocking Barriers Present)"
    lines.append(f"- **Compliance Status:** **{status_label}**")
    lines.append("")

    # Executive Summary Banner
    lines.append("## Executive Summary")
    lines.append("")

    if excluded or summary.get("has_excluded_barriers"):
        lines.append(
            "> **What-If Analysis Active:** Specific criteria were excluded from the compliance totals by user configuration. "
            "Their audit results and findings remain recorded below, but are omitted from the blocking barrier count and pass/fail verdict."
        )
        lines.append(">")
        lines.append(
            f"> - **Active Barriers:** **{summary.get('active_blocking', summary.get('blocking', 0))}** (counted toward verdict)\n"
            f"> - **Excluded Barriers:** **{summary.get('excluded_blocking', 0)}** (captured in what-if excluded bucket)"
        )
        lines.append(">")

    if stats.get("mode") == "remediated":
        lines.append(
            f"> **Remediation Progress:** Resolved **{stats['resolved_blocking']}** of "
            f"**{stats['before_blocking']}** blocking accessibility barriers "
            f"(**{stats['improvement_rate_pct']}% improvement**). "
            f"Remaining barriers: **{stats['after_blocking']}**."
        )
    else:
        status_word = "clean and passes active criteria" if is_compliant else "contains accessibility barriers that need attention"
        lines.append(
            f"> **Assessment:** This document {status_word}. "
            f"A total of **{summary.get('total', len(finding_objs))}** items were cataloged "
            f"(**{summary.get('blocking', 0)}** active barriers blocking compliance)."
        )
    lines.append("")

    # Full WCAG Conformance & Coverage Matrix Table
    sc_matrix = evaluate_sc_matrix(finding_objs, profile=profile, excluded_sc=excluded)
    lines.append("## WCAG Conformance & Coverage Matrix")
    lines.append("")
    lines.append(
        "This table provides full transparency across all WCAG 2.1 & 2.2 Level A and AA Success Criteria, "
        "documenting automated test results, human-in-the-loop review requirements, format applicability, "
        "and any what-if criteria exclusions."
    )
    lines.append("")
    lines.append("| Success Criterion | Title | Level | Principle | Status | Evaluation Details |")
    lines.append("|---|---|---|---|---|---|")

    for sc in sorted(sc_matrix.keys(), key=lambda s: [int(part) for part in s.split(".")]):
        entry = sc_matrix[sc]
        sc_link = f"[{sc}]({entry['url']})"
        p_name = dict(PRINCIPLES).get(entry["principle"], entry["principle"])
        stat_badge = f"[{entry['status'].value}]"
        note = entry["annotation"].replace("|", "\\|")
        lines.append(f"| {sc_link} | {entry['title']} | {entry['level']} | {p_name} | {stat_badge} | {note} |")
    lines.append("")

    # Group findings by Principle (POUR)
    findings_by_principle: Dict[str, List[Finding]] = {"1": [], "2": [], "3": [], "4": []}
    for fo in finding_objs:
        p_key = fo.sc.split(".")[0]
        if p_key in findings_by_principle:
            findings_by_principle[p_key].append(fo)

    for p_key, p_name in PRINCIPLES:
        p_findings = findings_by_principle[p_key]
        lines.append(f"## {p_key}. {p_name}")
        lines.append("")
        intro = POUR_INTROS.get(p_key, "")
        if intro:
            lines.append(intro)
            lines.append("")

        if not p_findings:
            lines.append(f"_No accessibility barriers detected under Principle {p_name}._")
            lines.append("")
            continue

        for idx, f in enumerate(p_findings, start=1):
            sc = f.sc
            sc_info = SC_META.get(sc, ("Accessibility Requirement", "A", f"{p_key} {p_name}", W3C_QUICKREF))
            sc_title, sc_level, _, sc_url = sc_info
            rule_id = f.rule_id
            sev = f.severity.upper()

            ex_badge = " [EXCLUDED FROM SUMMARY]" if f.excluded else ""
            lines.append(f"### {idx}. [{sev}]{ex_badge} {f.description}")
            lines.append("")
            if f.excluded:
                lines.append(
                    "> **What-If Note:** This finding belongs to a criterion excluded by user configuration. "
                    "It is shown here for inspection but excluded from blocking compliance totals."
                )
                lines.append("")

            lines.append(f"- **Success Criterion:** [WCAG SC {sc}: {sc_title} (Level {sc_level})]({sc_url})")
            lines.append(f"- **Location:** `{f.location or 'Unknown'}`")
            lines.append(f"- **Barrier Detected:** {RULE_BARRIER_EXPLANATIONS.get(rule_id, f.description)}")
            lines.append(f"- **Recommended Remediation:** {f.fix or 'Inspect and resolve.'}")
            lines.append(f"- **Who Benefits:** {WHO_MAP.get(sc, 'All readers gain improved access.')}")
            lines.append(f"- **Technical Evidence:** `{f.evidence}`")

            note = WORD_ASSISTANT_NOTES.get(rule_id)
            if note:
                lines.append(f"- **Word Accessibility Assistant Note:** {note}")

            if f.why_unfixable:
                lines.append(f"- **Why Software Cannot Automatically Fix This:** {f.why_unfixable}")

            if f.manual_steps:
                lines.append("- **Human in the Loop Remediation Protocol:**")
                for s_num, step in enumerate(f.manual_steps, start=1):
                    lines.append(f"  {s_num}. {step}")
            lines.append("")

    report_text = "\n".join(lines) + "\n"
    assert_social_model_language(report_text)
    return report_text
