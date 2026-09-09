"""Finding data model, summary metrics, and excluded-criteria partitioning for engine-a11y."""
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional

Severity = Literal["critical", "serious", "moderate", "minor"]

SEVERITY_ORDER = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
BLOCKING = ("critical", "serious")


@dataclass
class Finding:
    rule_id: str
    sc: str
    severity: Severity
    location: str
    description: str
    evidence: str = ""
    fixable: bool = False
    fix: str = ""
    why_unfixable: Optional[str] = None
    manual_steps: List[str] = field(default_factory=list)
    excluded: bool = False  # Set to True when user unchecks SC for what-if testing

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def blocking(self) -> bool:
        return self.severity in BLOCKING

    def sort_key(self):
        # Sort active findings before excluded, then by severity
        return (
            1 if self.excluded else 0,
            SEVERITY_ORDER.get(self.severity, 9),
            self.sc,
            self.location,
            self.rule_id,
        )


def finding_to_jsonable(f: Finding) -> Dict[str, Any]:
    return f.to_dict()


def findings_sorted(findings: List[Finding]) -> List[Finding]:
    return sorted(findings, key=lambda f: f.sort_key())


def summarize(findings: List[Finding]) -> Dict[str, Any]:
    """Summarize findings partitioning active vs user-excluded criteria."""
    active_by_sev = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    excluded_by_sev = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}

    active_count = 0
    excluded_count = 0

    for f in findings:
        if f.excluded:
            excluded_count += 1
            if f.severity in excluded_by_sev:
                excluded_by_sev[f.severity] += 1
        else:
            active_count += 1
            if f.severity in active_by_sev:
                active_by_sev[f.severity] += 1

    active_blocking = active_by_sev["critical"] + active_by_sev["serious"]
    excluded_blocking = excluded_by_sev["critical"] + excluded_by_sev["serious"]
    total = len(findings)

    return {
        "total": total,
        "active_total": active_count,
        "excluded_total": excluded_count,
        "blocking": active_blocking,
        "active_blocking": active_blocking,
        "excluded_blocking": excluded_blocking,
        "by_severity": active_by_sev,
        "pass": active_blocking == 0,
        "has_excluded_barriers": excluded_blocking > 0 or excluded_count > 0,
        "excluded": {
            "total": excluded_count,
            "blocking": excluded_blocking,
            "by_severity": excluded_by_sev,
        },
    }
