"""Remediation progress statistics (progress over perfection)."""
from typing import Any, Dict, List, Optional, Tuple, Union
from ..findings import Finding


def compute_progress_stats(
    before_summary: Dict[str, Any], after_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    b_total = before_summary.get("total", 0)
    b_blocking = before_summary.get("blocking", 0)

    if after_summary is None:
        return {
            "mode": "audit_only",
            "total_findings": b_total,
            "blocking_findings": b_blocking,
            "compliance_verdict": "PASS" if b_blocking == 0 else "ACTION REQUIRED",
        }

    a_total = after_summary.get("total", 0)
    a_blocking = after_summary.get("blocking", 0)
    resolved_blocking = max(0, b_blocking - a_blocking)
    improvement_rate = 100.0 if b_blocking == 0 else round((resolved_blocking / b_blocking) * 100.0, 1)

    return {
        "mode": "remediated",
        "before_total": b_total,
        "after_total": a_total,
        "before_blocking": b_blocking,
        "after_blocking": a_blocking,
        "resolved_blocking": resolved_blocking,
        "improvement_rate_pct": improvement_rate,
        "compliance_verdict": "PASS" if a_blocking == 0 else "PARTIAL REMEDIATION (MANUAL REVIEW NEEDED)",
    }


def _finding_key(f: Any) -> Tuple[str, str]:
    if isinstance(f, dict):
        return (str(f.get("rule_id", "")), str(f.get("location", "")))
    return (getattr(f, "rule_id", ""), getattr(f, "location", ""))


def _is_fixable(f: Any) -> bool:
    if isinstance(f, dict):
        return bool(f.get("fixable", False))
    return bool(getattr(f, "fixable", False))


def diff_findings(
    before_findings: List[Any],
    after_findings: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Compute finding-level diff between original and remediated states.

    Works with both Finding instances and dictionary representations.
    """
    if after_findings is None:
        auto_fixable = [f for f in before_findings if _is_fixable(f)]
        manual_only = [f for f in before_findings if not _is_fixable(f)]
        return {
            "mode": "audit_only",
            "resolved": [],
            "resolved_count": 0,
            "remaining": list(before_findings),
            "remaining_count": len(before_findings),
            "auto_fixable": auto_fixable,
            "manual_only": manual_only,
        }

    after_keys = {_finding_key(f) for f in after_findings}
    resolved = [f for f in before_findings if _finding_key(f) not in after_keys]
    remaining = list(after_findings)

    return {
        "mode": "remediated",
        "resolved": resolved,
        "resolved_count": len(resolved),
        "remaining": remaining,
        "remaining_count": len(remaining),
        "auto_fixable": [],
        "manual_only": [f for f in remaining if not _is_fixable(f)],
    }
