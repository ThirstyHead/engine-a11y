"""User-facing criteria configuration and 'what-if' filter engine.

Supports Markdown checklist [x] / [ ] format as primary, as well as YAML.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import yaml
from .findings import Finding
from .profile import WCAG_CATALOG

CHECKLIST_RE = re.compile(r"^\s*\[([ xX_-]?)\]\s*(\d+\.\d+\.\d+)")
KEY_VAL_RE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s*:\s*([a-zA-Z0-9_-]+)")


def load_criteria_config(path: Union[str, Path]) -> Tuple[Set[str], Set[str]]:
    """Parse text/YAML file and return (included_sc_set, excluded_sc_set).

    Supports:
    1. Markdown checklists: `[x] 1.1.1` (included) vs `[ ] 1.4.3` (excluded)
    2. Standard YAML: `criteria: { 1.1.1: true, 1.4.3: false }`
    3. Key-value lines: `1.4.3: false` / `1.4.3: off` / `1.4.3: disable`
    """
    p = Path(path)
    if not p.exists():
        return set(), set()

    raw_text = p.read_text(encoding="utf-8")
    included: Set[str] = set()
    excluded: Set[str] = set()

    # Try YAML first if text looks like a dict/yaml
    if raw_text.strip().startswith("criteria:") or ("\n  " in raw_text and ":" in raw_text):
        try:
            data = yaml.safe_load(raw_text)
            if isinstance(data, dict):
                crit_map = data.get("criteria", data)
                if isinstance(crit_map, dict):
                    for k, v in crit_map.items():
                        sc_str = str(k).strip()
                        if isinstance(v, bool):
                            (included if v else excluded).add(sc_str)
                        elif isinstance(v, str):
                            val = v.strip().lower()
                            if val in ("true", "yes", "on", "enable", "checked"):
                                included.add(sc_str)
                            elif val in ("false", "no", "off", "disable", "unchecked", "excluded"):
                                excluded.add(sc_str)
                    if included or excluded:
                        return included, excluded
        except Exception:
            pass

    # Line-by-line parsing for checklists or simple key-values
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Check for [x] or [ ]
        m_chk = CHECKLIST_RE.match(line)
        if m_chk:
            mark = m_chk.group(1).strip().lower()
            sc = m_chk.group(2).strip()
            if mark in ("x", "v"):
                included.add(sc)
            else:
                excluded.add(sc)
            continue

        # Check for key: value
        m_kv = KEY_VAL_RE.match(line)
        if m_kv:
            sc = m_kv.group(1).strip()
            val = m_kv.group(2).strip().lower()
            if val in ("true", "yes", "on", "enable"):
                included.add(sc)
            elif val in ("false", "no", "off", "disable", "excluded"):
                excluded.add(sc)

    return included, excluded


def apply_criteria_config(findings: List[Finding], excluded_sc: Set[str]) -> None:
    """Mark findings as excluded if their Success Criterion is in excluded_sc."""
    for f in findings:
        if f.sc in excluded_sc:
            f.excluded = True


def generate_criteria_template(out_path: Union[str, Path], format_type: str = "checklist") -> Path:
    """Generate a clean, user-editable criteria checklist file.

    Defaults to Markdown checklist format [x] / [ ] for intuitive editing.
    """
    target = Path(out_path)
    lines = [
        "# WCAG Accessibility Criteria Checklist",
        "# ----------------------------------------------------------------------",
        "# Instructions:",
        "# - Keep [x] checked to include a criterion in the compliance score (default).",
        "# - Uncheck any criterion with [ ] to audit it but exclude its failures from",
        "#   the summary blocking totals and pass/fail verdict (for what-if testing).",
        "#",
        "# What-If Example:",
        "#   [ ] 1.4.3 Contrast (Minimum)  <- What other barriers exist besides brand colors?",
        "# ----------------------------------------------------------------------",
        "",
    ]

    for sc in sorted(WCAG_CATALOG.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        meta = WCAG_CATALOG[sc]
        title = meta["title"]
        lvl = meta["level"]
        lines.append(f"[x] {sc} {title} (Level {lvl})")

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
