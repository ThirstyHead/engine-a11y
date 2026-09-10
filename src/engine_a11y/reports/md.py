"""Markdown report generator with full WCAG Conformance Matrix, Before/After Story, and What-If Excluded Bucket."""
from typing import Any, Dict, List, Optional, Set, Tuple
from .. import __version__
from ..findings import Finding
from ..profile import DocumentProfile, evaluate_sc_matrix
from .meta import POUR_INTROS, PRINCIPLES, SC_META, W3C_QUICKREF
from .stats import compute_progress_stats, diff_findings
from .tone import (
    HUMAN_IN_THE_LOOP_EXPLANATIONS,
    RULE_BARRIER_EXPLANATIONS,
    WHO_MAP,
    WORD_ASSISTANT_NOTES,
    assert_social_model_language,
    get_encouraging_progress_banner,
)


def _to_finding_objs(raw_list: List[Any], excluded: Set[str]) -> List[Finding]:
    objs: List[Finding] = []
    for f in raw_list:
        if isinstance(f, Finding):
            objs.append(f)
        else:
            objs.append(
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
    return objs


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

    finding_objs = _to_finding_objs(raw_findings, excluded)
    after_finding_objs = _to_finding_objs(after_result.get("findings", []), excluded) if after_result else None

    diff = diff_findings(finding_objs, after_finding_objs)
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
    if after_result:
        is_compliant = after_summary.get("pass", False) if after_summary else (diff["remaining_count"] == 0)

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

    total_initial = summary.get("total", len(finding_objs))
    resolved_count = diff["resolved_count"]
    remaining_count = diff["remaining_count"]

    banner_text = get_encouraging_progress_banner(resolved_count, remaining_count, total_initial)
    lines.append(f"> {banner_text}")
    lines.append("")

    # Scorecard Table
    lines.append("### Document Remediation Scorecard")
    lines.append("")
    lines.append("| Metric | Count | Details |")
    lines.append("|---|:---:|---|")
    lines.append(f"| **Original Barriers Detected** | **{total_initial}** | Initial accessibility barriers found |")
    lines.append(f"| **Automatically Fixed & Incorporated** | **{resolved_count}** | Resolved by automated remediation in new document |")
    lines.append(f"| **Remaining Human Actions** | **{remaining_count}** | Requires author review or manual verification |")
    
    pct_str = f"{stats.get('improvement_rate_pct', 0.0)}%" if stats.get("mode") == "remediated" else "N/A (Audit Only)"
    lines.append(f"| **Remediation Improvement** | **{pct_str}** | Progress toward full accessibility |")
    lines.append("")

    # Fixes Incorporated Section
    if diff["resolved"]:
        lines.append("## Fixes Incorporated into Remediated Document")
        lines.append("")
        lines.append(
            "The following accessibility fixes were **automatically applied and verified** in the remediated document. "
            "Your original file remains untouched."
        )
        lines.append("")
        for idx, f in enumerate(diff["resolved"], start=1):
            sc = f.sc
            sc_info = SC_META.get(sc, ("Accessibility Requirement", "A", "", W3C_QUICKREF))
            lines.append(f"### {idx}. ✅ [FIXED] {f.description}")
            lines.append(f"- **Item / Location:** `{f.location or 'Document-level'}`")
            lines.append(f"- **Success Criterion:** [WCAG SC {sc}: {sc_info[0]} (Level {sc_info[1]})]({sc_info[3]})")
            lines.append(f"- **Remediation Action Applied:** {f.fix or 'Automated structural repair applied.'}")
            lines.append(f"- **Who Benefits:** {WHO_MAP.get(sc, 'All readers receive improved document access.')}")
            lines.append("")

    # Action Checklist for Human in the Loop
    if remaining_count > 0:
        lines.append("## Action Checklist: Human-in-the-Loop Next Steps")
        lines.append("")
        lines.append(
            "> **Why can't software fix everything?** Digital accessibility is fundamentally about human communication. "
            "Automated tools cannot guess author intent, summarize charts without risking factual distortion, or rewrite "
            "ambiguous links. These remaining items require author review to ensure full and genuine accessibility."
        )
        lines.append("")
        for idx, f in enumerate(diff["remaining"], start=1):
            sc = f.sc
            sc_info = SC_META.get(sc, ("Accessibility Requirement", "A", "", W3C_QUICKREF))
            why_unfixable = f.why_unfixable or HUMAN_IN_THE_LOOP_EXPLANATIONS.get(
                f.rule_id, "Requires human editorial judgment or domain-specific context."
            )
            lines.append(f"### {idx}. ⚠️ [ACTION REQUIRED] {f.description}")
            lines.append(f"- [ ] **Task:** Resolve `{f.description}` at `{f.location or 'Document'}`")
            lines.append(f"- **Success Criterion:** [WCAG SC {sc}: {sc_info[0]} (Level {sc_info[1]})]({sc_info[3]})")
            lines.append(f"- **Why Automated Software Cannot Fix This:** {why_unfixable}")
            if f.manual_steps:
                lines.append("- **Step-by-Step Instructions:**")
                for s_num, step in enumerate(f.manual_steps, start=1):
                    lines.append(f"  {s_num}. {step}")
            else:
                lines.append(f"- **Recommended Action:** {f.fix or 'Review element and update in your authoring software.'}")
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
    resolved_keys = {(f.rule_id, f.location) for f in diff["resolved"]}
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

            if (f.rule_id, f.location) in resolved_keys:
                status_chip = "[RESOLVED BY AUTO-REMEDIATION]"
            elif f.excluded:
                status_chip = "[EXCLUDED FROM VERDICT]"
            else:
                status_chip = "[ACTION REQUIRED - HUMAN IN THE LOOP]"

            lines.append(f"### {idx}. [{sev}] {status_chip} {f.description}")
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
