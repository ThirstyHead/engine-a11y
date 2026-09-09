"""Author-intent triage state machine shared across document formats."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TriageItem:
    rule_id: str
    location: str
    description: str
    prompt: str
    current_value: Optional[str] = None
    action: str = "input"  # "input", "select", "boolean"
    choices: Optional[List[str]] = None
    resolved_value: Optional[Any] = None


class TriageSession:
    """Manages author-intent decision points for document accessibility."""

    def __init__(
        self,
        findings: List[Dict[str, Any]],
        doc_model: Optional[Any] = None,
        file_path: Optional[str] = None,
    ):
        self.findings = findings
        self.doc_model = doc_model
        self.file_path = file_path
        self.items: List[TriageItem] = []
        self._build_items()

    def _build_items(self) -> None:
        for f in self.findings:
            rule_id = f.get("rule_id", "")
            loc = f.get("location", "")
            msg = f.get("message") or f.get("description", "")

            if rule_id in ("title-missing", "doc-title-missing"):
                self.items.append(
                    TriageItem(
                        rule_id=rule_id,
                        location=loc,
                        description=msg or "Document title is missing.",
                        prompt="Enter a descriptive document title (or press Enter to auto-generate):",
                        action="input",
                    )
                )
            elif rule_id in ("language-missing", "language-malformed", "doc-language-missing"):
                self.items.append(
                    TriageItem(
                        rule_id=rule_id,
                        location=loc,
                        description=msg or "Document language is missing or invalid.",
                        prompt="Enter primary language BCP-47 tag (e.g. 'en-US', 'fr-FR'):",
                        action="input",
                        current_value=f.get("evidence", ""),
                    )
                )
            elif rule_id in (
                "image-alt-missing",
                "figure-without-alt",
                "media-alt-missing",
                "graphic-missing-alt",
            ):
                self.items.append(
                    TriageItem(
                        rule_id=rule_id,
                        location=loc,
                        description=msg or "Visual asset is missing alternative text.",
                        prompt=f"Enter alternative text for asset at {loc} (or 'decorative'/'artifact'):",
                        action="input",
                    )
                )
            elif rule_id in ("outline-missing", "bookmarks-missing"):
                self.items.append(
                    TriageItem(
                        rule_id=rule_id,
                        location=loc,
                        description=msg or "Document has headings but no outline/bookmarks navigation.",
                        prompt="Generate outline / bookmarks from heading structure? (y/n):",
                        action="boolean",
                        choices=["y", "n"],
                    )
                )

    def get_pending_items(self) -> List[TriageItem]:
        return [item for item in self.items if item.resolved_value is None]

    def resolve_item(self, index: int, value: Any) -> None:
        if 0 <= index < len(self.items):
            self.items[index].resolved_value = value

    def to_context_overrides(self) -> Dict[str, Any]:
        overrides: Dict[str, Any] = {}
        for item in self.items:
            if item.resolved_value is None:
                continue
            val = item.resolved_value
            if item.rule_id in ("title-missing", "doc-title-missing"):
                if isinstance(val, str) and val.strip():
                    overrides["title"] = val.strip()
            elif item.rule_id in ("language-missing", "language-malformed", "doc-language-missing"):
                if isinstance(val, str) and val.strip():
                    overrides["default_language"] = val.strip()
            elif item.rule_id in (
                "image-alt-missing",
                "figure-without-alt",
                "media-alt-missing",
                "graphic-missing-alt",
            ):
                if "alt_map" not in overrides:
                    overrides["alt_map"] = {}
                overrides["alt_map"][item.location] = str(val).strip()
        return overrides
