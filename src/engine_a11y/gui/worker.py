"""Background QThread worker base class for auditing and bulk remediation."""
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from PySide6.QtCore import QThread, Signal
from ..criteria_config import apply_criteria_config
from ..findings import Finding, summarize
from ..profile import DocumentProfile
from ..reports.html import render_html
from ..reports.md import render_md
from ..reports.pdf import render_pdf
from .models import BatchItem


class BaseBatchWorker(QThread):
    item_started = Signal(int, int, str)  # (item_idx, total_items, file_name)
    item_progress = Signal(int, str)  # (item_idx, step_name)
    item_finished = Signal(int, str, int, float)  # (item_idx, status, findings_count, score)
    all_completed = Signal(int, int)  # (total_processed, total_errors)
    error_occurred = Signal(int, str)  # (item_idx, error_message)

    def __init__(
        self,
        items: List[BatchItem],
        out_dir: Path | str,
        formats: List[str],
        audit_func: Callable[[Path], Dict[str, Any]],
        remediate_func: Optional[Callable[[Path, Path], Any]] = None,
        profile: Optional[DocumentProfile] = None,
        excluded_sc: Optional[Set[str]] = None,
        theme: str = "light",
        auto_fix: bool = False,
    ):
        super().__init__()
        self.items = items
        self.out_dir = Path(out_dir)
        self.formats = formats
        self.audit_func = audit_func
        self.remediate_func = remediate_func
        self.profile = profile
        self.excluded_sc = set(excluded_sc or [])
        self.theme = theme
        self.auto_fix = auto_fix
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> None:
        try:
            self.out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.error_occurred.emit(0, f"Cannot create output directory '{self.out_dir}': {exc}")
            self.all_completed.emit(0, len(self.items))
            return

        total = len(self.items)
        processed = 0
        errors = 0

        for idx, item in enumerate(self.items):
            if self._stop_requested:
                break

            item.status = "Auditing"
            self.item_started.emit(idx, total, item.path.name)

            try:
                self.item_progress.emit(idx, "Auditing document...")
                audit_before = self.audit_func(item.path)
                raw_findings = audit_before.get("findings", [])

                # Convert to Finding objects and apply user criteria exclusions
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
                                excluded=f.get("excluded", False),
                            )
                        )
                apply_criteria_config(finding_objs, self.excluded_sc)
                summary = summarize(finding_objs)
                audit_before["summary"] = summary
                audit_before["findings"] = [f.to_dict() for f in finding_objs]

                item.findings_count = summary.get("active_total", len(finding_objs))
                item.critical_count = summary.get("by_severity", {}).get("critical", 0)

                # Score calculation based on active barriers
                if item.findings_count == 0:
                    item.score = 100.0
                else:
                    by_sev = summary.get("by_severity", {})
                    penalties = (
                        item.critical_count * 20.0
                        + by_sev.get("serious", 0) * 10.0
                        + by_sev.get("moderate", 0) * 5.0
                        + by_sev.get("minor", 0) * 2.0
                    )
                    item.score = max(0.0, round(100.0 - penalties, 1))

                # Optional remediation
                audit_after = None
                if self.auto_fix and self.remediate_func:
                    self.item_progress.emit(idx, "Applying remediation...")
                    remediated_p = self.out_dir / f"{item.path.stem}-remediated{item.path.suffix}"
                    self.remediate_func(item.path, remediated_p)
                    item.remediated_path = remediated_p
                    audit_after = self.audit_func(remediated_p)
                    raw_after_findings = audit_after.get("findings", [])
                    after_objs = [
                        f if isinstance(f, Finding) else Finding(
                            rule_id=f.get("rule_id", ""),
                            sc=f.get("sc", "1.1.1"),
                            severity=f.get("severity", "moderate"),
                            location=f.get("location", ""),
                            description=f.get("description", ""),
                        )
                        for f in raw_after_findings
                    ]
                    apply_criteria_config(after_objs, self.excluded_sc)
                    audit_after["summary"] = summarize(after_objs)
                    audit_after["findings"] = [f.to_dict() for f in after_objs]

                # Generate reports
                stem = item.path.stem
                md_text = render_md(
                    audit_before,
                    after_result=audit_after,
                    source_path=str(item.path),
                    profile=self.profile,
                    excluded_sc=self.excluded_sc,
                )

                if "md" in self.formats:
                    self.item_progress.emit(idx, "Writing Markdown report...")
                    (self.out_dir / f"{stem}-report.md").write_text(md_text, encoding="utf-8")

                if "html" in self.formats:
                    self.item_progress.emit(idx, "Writing HTML5 report...")
                    html_doc = render_html(md_text, theme=self.theme)
                    (self.out_dir / f"{stem}-report.html").write_text(html_doc, encoding="utf-8")

                    if "pdf" in self.formats:
                        self.item_progress.emit(idx, "Compiling accessible PDF report...")
                        render_pdf(html_doc, out_path=self.out_dir / f"{stem}-report.pdf")

                item.status = "Complete"
                self.item_finished.emit(idx, item.status, item.findings_count, item.score)
                processed += 1
            except Exception as exc:
                item.status = "Error"
                errors += 1
                self.error_occurred.emit(idx, str(exc))

        self.all_completed.emit(processed, errors)
