# Engine-A11y Refactoring Implementation Plan

> **For Hermes:** Use `subagent-driven-development` skill to implement this plan task-by-task.

**Goal:** Extract and consolidate the shared accessibility infrastructure (findings data structures with "what-if" excluded buckets, contrast algorithms, source immutability, full WCAG 2.1/2.2 criteria catalog, user-editable criteria configuration files, document-specific conformance profiles, multi-format reporting with full SC coverage matrices, triage state machine, and desktop GUI) from `pdf-a11y`, `docx-a11y`, `pptx-a11y`, and `xslx-a11y` into a standalone, modular core library `/Users/scott/code/local/engine-a11y`.

**Architecture:** `engine-a11y` (`engine_a11y`) serves as the headless foundation providing format-agnostic data structures, contrast math, report renderers, triage workflows, and GUI widgets. Crucially, it provides:
1. A comprehensive WCAG SC Catalog (all Level A & AA criteria).
2. A `DocumentProfile` mechanism for format-specific automated, manual, and non-applicable declarations.
3. A simple text-based configuration file (`a11y-criteria.yaml` / `.a11y-criteria.txt` or Markdown checklist) that enables end users to check/uncheck criteria for "what-if" impact modeling. Unchecked criteria (e.g. color contrast) are still audited and reported in the conformance matrix, but their failures are partitioned into an `"excluded"` bucket, omitting them from the final blocking totals and compliance verdict.
4. Conformance matrix and multi-format report renderers displaying all criteria with transparent status annotations (`PASS`, `FAIL`, `MANUAL_REVIEW`, `UNCHECKED`, `NOT_APPLICABLE`, and `[EXCLUDED]`).

**Tech Stack:** Python 3.10+, PySide6 6.5+, PyMuPDF 1.24+, Pikepdf 9.0+, Markdown 3.6+, PyYAML 6.0+, wcag-contrast-ratio 0.9+, pytest, setuptools.

---

## Current Context & Assumptions

1. **Existing Projects:**
   - `/Users/scott/code/local/pdf-a11y`: Audits and remediates PDF documents via `pikepdf`, `pymupdf`, and `pdfplumber`.
   - `/Users/scott/code/local/docx-a11y`: Audits and remediates Word `.docx` documents via `python-docx-ng`.
   - `/Users/scott/code/local/pptx-a11y`: Audits and remediates PowerPoint `.pptx` presentations via `python-pptx`.
   - `/Users/scott/code/local/xslx-a11y`: Audits and remediates Excel `.xlsx` workbooks via `openpyxl`.

2. **User Story: Text-Based Criteria Filter & "What-If" Analysis:**
   - *Problem:* An organization may be actively redesigning brand colors, awaiting copy team image descriptions, or testing alternative templates. They need to know: *"If we assume contrast is about to be solved by our upcoming brand update, what other accessibility barriers exist in this document right now?"*
   - *Requirement:* A simple, user-editable text file (e.g. `a11y-criteria.yaml`, `.a11y-criteria.txt`, or checklist format) where users can easily toggle SCs (e.g. `1.4.3: false` or `[ ] 1.4.3 Contrast`).
   - *Semantics:*
     - The tool **does not stop auditing** the unchecked SC; full checks still execute.
     - All findings for unchecked SCs are captured and rendered in the report and the Conformance Matrix (tagged `[EXCLUDED: FAIL]` or `[EXCLUDED: PASS]`).
     - Any findings belonging to unchecked SCs are placed into an `"excluded"` bucket.
     - Excluded findings are deducted/omitted from `blocking_count`, allowing the compliance pass/fail verdict to reflect active criteria while transparently communicating the "what-if" results.

3. **Commonalities & Core Architecture to Extract:**
   - `findings.py`: `Finding` (with `excluded` flag), `Severity`, `SEVERITY_ORDER`, `BLOCKING`, `findings_sorted()`, `summarize()` (with `active` vs `excluded` buckets).
   - `criteria_config.py`: Parser and generator for user criteria config files (YAML, text checklist, CLI generator).
   - `contrast.py`: Relative luminance, contrast ratio calculation, WCAG AA thresholds, deterministic color adjuster (`adjust_color_for_contrast`).
   - `immutability.py`: Pre/post SHA-256 validation, `assert_source_unchanged`, `assert_not_same_path`, non-destructive output path generation.
   - `profile.py`: `DocumentProfile`, `SCStatus`, `evaluate_sc_matrix` (supports format rules and user-excluded criteria).
   - `enrich.py` & `sc_cache.json`: Offline WCAG criterion metadata cache and MCP client connector.
   - `reports/`:
     - `meta.py`: Canonical catalog of ALL WCAG 2.1 & 2.2 Level A/AA criteria, POUR hierarchy, W3C Understanding URLs.
     - `tone.py`: Social model tone assertions (`assert_social_model_language`), `WHO_MAP`, assistant guidance notes.
     - `stats.py`: Audit statistics, remediation progress, and active vs excluded summaries.
     - `theme.py` & `themes/`: 6 SMACSS themes (`light`, `dark`, `high-contrast`, `ocean`, `forest`, `print`) and layout CSS layers.
     - `md.py`: Canonical Markdown report generator with Complete WCAG SC Conformance Matrix and What-If Excluded Banner.
     - `html.py`: Accessible, standalone HTML5 report generator with inlined CSS and landmarks.
     - `pdf.py`: Tagged accessible PDF report renderer via PyMuPDF Story + Pikepdf.
   - `triage.py`: `TriageItem`, `TriageSession`, interactive CLI prompt driver.
   - `gui/`: Reusable PySide6 GUI components (`app.py`, `main_window.py`, `models.py`, `theme.py`, `triage_dialog.py`, `worker.py`).
   - `cli.py`: Unified CLI parser builder (`build_common_parser`) and standard pipeline runner (`run_cli_pipeline`) with `--criteria` and `--init-criteria`.

---

## Step-by-Step Implementation Tasks

### Phase 1: Project Setup & Package Scaffolding

#### Task 1.1: Initialize `engine-a11y` package configuration (`pyproject.toml`)
**Objective:** Create the modern `pyproject.toml` for `engine-a11y` specifying build system, dependencies (`pyyaml` included for criteria configs), optional dependencies (`gui`, `dev`, `all`), and package metadata.

**Files:**
- Create: `/Users/scott/code/local/engine-a11y/pyproject.toml`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/__init__.py`

**Step 1: Write `pyproject.toml` and `__init__.py`**
Create `/Users/scott/code/local/engine-a11y/pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "engine-a11y"
version = "0.1.0"
description = "Core accessibility engine, data models, contrast algorithms, reporting, triage, and GUI shared across format-specific accessibility tools"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "a11y contributors" }]
keywords = ["accessibility", "wcag", "a11y", "contrast", "reporting", "triage"]
dependencies = [
    "wcag-contrast-ratio>=0.9,<1",
    "markdown>=3.6,<4",
    "pymupdf>=1.24",
    "pikepdf>=9.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
gui = [
    "PySide6>=6.5",
]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-qt>=4.4.0",
]
all = [
    "engine-a11y[dev,gui]",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
engine_a11y = [
    "sc_cache.json",
    "reports/themes/**/*.css",
    "reports/themes/**/*.json",
    "reports/themes/**/*.md",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Create `/Users/scott/code/local/engine-a11y/src/engine_a11y/__init__.py`:
```python
"""engine-a11y: Core engine for document accessibility auditing and remediation."""

__version__ = "0.1.0"
```

**Step 2: Verify package installation**
Run:
```bash
cd /Users/scott/code/local/engine-a11y
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[all]"
python -c "import engine_a11y; print(engine_a11y.__version__)"
```
Expected output: `0.1.0`

**Step 3: Commit**
```bash
cd /Users/scott/code/local/engine-a11y
git add pyproject.toml src/engine_a11y/__init__.py
git commit -m "feat(scaffold): initialize engine-a11y package and dependencies"
```

---

### Phase 2: Core Data Models & Excluded Summary Buckets (`engine_a11y.findings`)

#### Task 2.1: Implement `engine_a11y.findings` with Excluded Support
**Objective:** Create the canonical `Finding` data class with `excluded: bool = False`, `Severity` type, sorting functions, and `summarize()` that partitions active vs excluded findings for "what-if" modeling.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_findings.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/findings.py`

**Step 1: Write failing test**
Create `/Users/scott/code/local/engine-a11y/tests/test_findings.py`:
```python
import pytest
from engine_a11y.findings import Finding, findings_sorted, summarize

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
    assert d["excluded"] is False

def test_summarize_with_excluded_bucket():
    # Active findings
    f1 = Finding("image-alt-missing", "1.1.1", "critical", "loc1", "desc1")
    f2 = Finding("heading-skipped", "1.3.1", "serious", "loc2", "desc2")
    # Excluded finding (e.g. contrast unchecked by user in what-if test)
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
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_findings.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'engine_a11y.findings'`)

**Step 3: Implement `src/engine_a11y/findings.py`**
```python
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
```

**Step 4: Run test to verify pass**
Run: `pytest tests/test_findings.py -v`
Expected: 3 passed.

**Step 5: Commit**
```bash
git add tests/test_findings.py src/engine_a11y/findings.py
git commit -m "feat(findings): add excluded flag and partitioned summary metrics for what-if testing"
```

---

### Phase 3: Simple Text-Based Criteria Configuration (`engine_a11y.criteria_config`)

#### Task 3.1: Implement User Criteria Config Parser and Generator
**Objective:** Provide a user-friendly configuration engine that reads simple YAML, JSON, or checklist `.txt`/`.md` files (allowing users to check/uncheck SCs), applies the exclusions to findings, and exports baseline configuration templates.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_criteria_config.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/criteria_config.py`

**Step 1: Write failing test**
Create `/Users/scott/code/local/engine-a11y/tests/test_criteria_config.py`:
```python
import pytest
from pathlib import Path
from engine_a11y.criteria_config import (
    load_criteria_config,
    apply_criteria_config,
    generate_criteria_template,
)
from engine_a11y.findings import Finding

def test_load_yaml_criteria_config(tmp_path):
    cfg_file = tmp_path / "a11y-criteria.yaml"
    cfg_file.write_text("""
criteria:
  1.1.1: true
  1.3.1: true
  1.4.3: false  # Unchecked for what-if testing
  2.4.2: enable
  2.4.4: disable
""")
    included, excluded = load_criteria_config(cfg_file)
    assert "1.1.1" in included
    assert "1.3.1" in included
    assert "2.4.2" in included
    assert "1.4.3" in excluded
    assert "2.4.4" in excluded

def test_load_text_checklist_format(tmp_path):
    # Support simple text/markdown checklist [x] vs [ ]
    txt_file = tmp_path / "criteria.txt"
    txt_file.write_text("""
# Accessibility Criteria Checklist
[x] 1.1.1 Non-text Content
[x] 1.3.1 Info and Relationships
[ ] 1.4.3 Contrast (Minimum) - Brand colors in flux
[ ] 2.4.4 Link Purpose
""")
    included, excluded = load_criteria_config(txt_file)
    assert "1.1.1" in included
    assert "1.3.1" in included
    assert "1.4.3" in excluded
    assert "2.4.4" in excluded

def test_apply_criteria_config():
    f1 = Finding("image-alt-missing", "1.1.1", "critical", "loc1", "desc")
    f2 = Finding("contrast-low", "1.4.3", "serious", "loc2", "desc")
    findings = [f1, f2]

    apply_criteria_config(findings, excluded_sc={"1.4.3"})
    assert f1.excluded is False
    assert f2.excluded is True

def test_generate_criteria_template(tmp_path):
    out_file = tmp_path / "template.yaml"
    generate_criteria_template(out_file)
    assert out_file.exists()
    content = out_file.read_text()
    assert "1.1.1: true" in content
    assert "1.4.3: true" in content
    assert "# Set to false to exclude from summary totals for what-if modeling" in content
```

**Step 2: Run test to verify failure**
Run: `pytest tests/test_criteria_config.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'engine_a11y.criteria_config'`)

**Step 3: Implement `src/engine_a11y/criteria_config.py`**
```python
"""User-facing criteria configuration and 'what-if' filter engine."""
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import yaml
from .findings import Finding

CHECKLIST_RE = re.compile(r"^\s*\[([ xX_-]?)\]\s*(\d+\.\d+\.\d+)")
KEY_VAL_RE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s*:\s*([a-zA-Z0-9_-]+)")


def load_criteria_config(path: Union[str, Path]) -> Tuple[Set[str], Set[str]]:
    """Parse text/YAML file and return (included_sc_set, excluded_sc_set).

    Supports:
    1. Standard YAML: `criteria: { 1.1.1: true, 1.4.3: false }`
    2. Key-value lines: `1.4.3: false` / `1.4.3: off` / `1.4.3: disable`
    3. Markdown checklists: `[x] 1.1.1` vs `[ ] 1.4.3`
    """
    p = Path(path)
    if not p.exists():
        return set(), set()

    raw_text = p.read_text(encoding="utf-8")
    included: Set[str] = set()
    excluded: Set[str] = set()

    # Try YAML first
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

    # Fallback to line-by-line parsing for checklists or simple key-values
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


def generate_criteria_template(out_path: Union[str, Path]) -> Path:
    """Generate a clean, user-editable criteria checklist YAML file."""
    from .profile import WCAG_CATALOG

    target = Path(out_path)
    lines = [
        "# Accessibility Criteria Configuration",
        "# ---------------------------------------",
        "# Instructions:",
        "# - Set any criterion to 'true' to include it in the compliance score (default).",
        "# - Set any criterion to 'false' (or comment it out) to exclude it from blocking",
        "#   totals and pass/fail verdicts.",
        "# - Unchecked criteria are STILL audited, and failures appear in the report,",
        "#   but they are placed into an 'Excluded' bucket for 'what-if' modeling.",
        "#",
        "# Example What-If Testing:",
        "#   1.4.3: false   # 'Our brand colors will be updated soon. What else is broken?'",
        "",
        "criteria:",
    ]

    for sc in sorted(WCAG_CATALOG.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        meta = WCAG_CATALOG[sc]
        title = meta["title"]
        lvl = meta["level"]
        lines.append(f"  {sc}: true  # {title} (Level {lvl})")

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
```

**Step 4: Run test to verify pass**
Run: `pytest tests/test_criteria_config.py -v`
Expected: 4 passed.

**Step 5: Commit**
```bash
git add src/engine_a11y/criteria_config.py tests/test_criteria_config.py
git commit -m "feat(config): add user criteria config parser, checklist reader, and template generator"
```

---

### Phase 4: Contrast Math & Luminosity Optimization (`engine_a11y.contrast`)

#### Task 4.1: Implement `engine_a11y.contrast`
**Objective:** Provide standard WCAG relative luminance math, contrast ratio calculations, compliance checks, and deterministic luminosity color scaling (`adjust_color_for_contrast`).

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_contrast.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/contrast.py`

*(Same copy-pasteable implementation and tests as previously detailed)*

---

### Phase 5: Document Integrity & Immutability Engine (`engine_a11y.immutability`)

#### Task 5.1: Implement `engine_a11y.immutability`
**Objective:** Provide SHA-256 hash calculation, provenance validation, input immutability assertions, and non-destructive destination path calculation.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_immutability.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/immutability.py`

*(Same copy-pasteable implementation and tests as previously detailed)*

---

### Phase 6: Document Profiles & Complete WCAG Catalog with Exclusions (`engine_a11y.profile`)

#### Task 6.1: Implement Complete WCAG Catalog and Excluded SC Support
**Objective:** Update `engine_a11y.profile` so `evaluate_sc_matrix` accepts `excluded_sc: Set[str]` to tag excluded criteria in the matrix and provide annotations for "what-if" modeling.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_profile.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/profile.py`

**Step 1: Write failing test**
Create `/Users/scott/code/local/engine-a11y/tests/test_profile.py`:
```python
import pytest
from engine_a11y.profile import (
    DocumentProfile,
    SCStatus,
    evaluate_sc_matrix,
    get_complete_wcag_catalog,
)
from engine_a11y.findings import Finding

def test_evaluate_sc_matrix_with_excluded_sc():
    profile = DocumentProfile(
        name="Word Document",
        doc_type="Document",
        automated_sc={"1.1.1": "Alt text check", "1.4.3": "Contrast check"},
    )
    # Finding on contrast
    f = Finding(rule_id="contrast-low", sc="1.4.3", severity="serious", location="P1", description="Low contrast", excluded=True)
    findings = [f]

    # User excluded 1.4.3 in criteria config
    matrix = evaluate_sc_matrix(findings=findings, profile=profile, excluded_sc={"1.4.3"})

    assert matrix["1.4.3"]["is_excluded"] is True
    assert matrix["1.4.3"]["status"] == SCStatus.FAIL
    assert "[EXCLUDED FROM SUMMARY]" in matrix["1.4.3"]["annotation"]
```

**Step 2: Implement updated `src/engine_a11y/profile.py`**
In `src/engine_a11y/profile.py`, update `evaluate_sc_matrix`:
```python
def evaluate_sc_matrix(
    findings: List[Finding],
    profile: Optional[DocumentProfile] = None,
    excluded_sc: Optional[Set[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Generate exhaustive status mapping for all WCAG criteria, noting user exclusions."""
    p = profile or DocumentProfile()
    excluded = excluded_sc or set()
    findings_by_sc: Dict[str, List[Finding]] = {}
    for f in findings:
        findings_by_sc.setdefault(f.sc, []).append(f)

    matrix: Dict[str, Dict[str, Any]] = {}

    for sc, meta in WCAG_CATALOG.items():
        title = meta["title"]
        level = meta["level"]
        principle = meta["principle"]
        url = f"{W3C_UNDERSTANDING}{meta['slug']}.html"

        sc_findings = findings_by_sc.get(sc, [])
        is_user_excluded = sc in excluded

        if sc in p.automated_sc:
            if sc_findings:
                status = SCStatus.FAIL
                prefix = "[EXCLUDED FROM SUMMARY] " if is_user_excluded else ""
                annotation = f"{prefix}Automated check detected {len(sc_findings)} barrier(s): {p.automated_sc[sc]}"
            else:
                status = SCStatus.PASS
                prefix = "[EXCLUDED FROM SUMMARY] " if is_user_excluded else ""
                annotation = f"{prefix}Automated check passed: {p.automated_sc[sc]}"
        elif sc in p.human_in_the_loop_sc:
            status = SCStatus.MANUAL_REVIEW
            annotation = p.human_in_the_loop_sc[sc]
        elif sc in p.not_applicable_sc:
            status = SCStatus.NOT_APPLICABLE
            annotation = p.not_applicable_sc[sc]
        elif sc in p.unchecked_sc:
            status = SCStatus.UNCHECKED
            annotation = p.unchecked_sc[sc]
        else:
            if sc_findings:
                status = SCStatus.FAIL
                annotation = f"Detected {len(sc_findings)} finding(s)."
            else:
                status = SCStatus.UNCHECKED
                annotation = "Not evaluated by this automated tool."

        if is_user_excluded:
            annotation += " (Excluded from compliance score via user criteria configuration)"

        matrix[sc] = {
            "sc": sc,
            "title": title,
            "level": level,
            "principle": principle,
            "url": url,
            "status": status,
            "annotation": annotation,
            "findings": sc_findings,
            "is_excluded": is_user_excluded,
        }

    return matrix
```

---

### Phase 7: Reporting Infrastructure with What-If Excluded Banners (`reports.md`, `html`, `pdf`)

#### Task 7.1: Implement Markdown Report with "What-If" Excluded Findings Section
**Objective:** Ensure `render_md` displays the "What-If Analysis" banner when user exclusions are present, explicitly reporting active vs excluded totals, badge markings (`[EXCLUDED: FAIL]`), and separate finding tables.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_reports_what_if.py`
- Modify: `/Users/scott/code/local/engine-a11y/src/engine_a11y/reports/md.py`

**Step 1: Write failing test**
Create `/Users/scott/code/local/engine-a11y/tests/test_reports_what_if.py`:
```python
import pytest
from engine_a11y.reports.md import render_md
from engine_a11y.findings import summarize

def test_render_md_what_if_banner():
    result = {
        "file": "deck.pptx",
        "sha256": "abcdef",
        "summary": {
            "total": 3,
            "active_total": 1,
            "excluded_total": 2,
            "blocking": 0,
            "active_blocking": 0,
            "excluded_blocking": 2,
            "pass": True,
            "has_excluded_barriers": True,
            "excluded": {"total": 2, "blocking": 2, "by_severity": {"serious": 2}},
        },
        "findings": [
            {"rule_id": "title-missing", "sc": "2.4.2", "severity": "minor", "location": "Doc", "description": "Title minor", "excluded": False},
            {"rule_id": "contrast-low", "sc": "1.4.3", "severity": "serious", "location": "Slide 1", "description": "Color contrast low", "excluded": True},
        ],
    }
    md = render_md(result, excluded_sc={"1.4.3"})
    assert "### What-If Modeling Notice" in md
    assert "Excluded Criteria:** `1.4.3`" in md
    assert "Excluded Barriers:** **2**" in md
    assert "Compliance Verdict:** **COMPLIANT (Active Criteria Only)**" in md
```

**Step 2: Update `src/engine_a11y/reports/md.py`**
Incorporate the What-If Notice and excluded finding indicators:
```python
    # What-If Excluded Banner
    if summary.get("has_excluded_barriers") or excluded_sc:
        lines.append("### What-If Modeling Notice")
        lines.append("")
        ex_sc_list = ", ".join(f"`{s}`" for s in sorted(excluded_sc or [])) or "None"
        lines.append(
            f"> **What-If Analysis Active:** Specific criteria ({ex_sc_list}) have been excluded "
            "from the compliance totals by user configuration. Their audit results and findings "
            "remain recorded below, but are omitted from the blocking barrier count and pass/fail verdict."
        )
        lines.append(">")
        ex_stats = summary.get("excluded", {})
        lines.append(
            f"> - **Active Barriers:** **{summary.get('active_blocking', 0)}** (counted toward verdict)\n"
            f"> - **Excluded Barriers:** **{ex_stats.get('blocking', 0)}** (captured in excluded bucket)\n"
            f"> - **Adjusted Compliance Verdict:** **{'COMPLIANT' if summary.get('pass') else 'NON-COMPLIANT'}**"
        )
        lines.append("")
```

---

### Phase 8: CLI Integration with `--criteria` and `--init-criteria` (`engine_a11y.cli`)

#### Task 8.1: Support Criteria Configuration in CLI Pipeline
**Objective:** Add `--criteria <path>` to load user configuration and `--init-criteria [path]` to generate an editable template.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_cli_criteria.py`
- Modify: `/Users/scott/code/local/engine-a11y/src/engine_a11y/cli.py`

**Step 1: Write failing test**
Create `/Users/scott/code/local/engine-a11y/tests/test_cli_criteria.py`:
```python
import pytest
from engine_a11y.cli import build_common_parser

def test_criteria_cli_arguments():
    parser = build_common_parser("doc-a11y", "Audit docs", "docx")
    args = parser.parse_args(["sample.docx", "--criteria", "my-criteria.yaml"])
    assert args.criteria == "my-criteria.yaml"

    args_init = parser.parse_args(["--init-criteria"])
    assert args_init.init_criteria is not None
```

**Step 2: Update `src/engine_a11y/cli.py`**
In `build_common_parser`:
```python
    parser.add_argument(
        "--criteria",
        default=None,
        help="Path to user criteria configuration or checklist file (YAML or TXT) to include/exclude criteria",
    )
    parser.add_argument(
        "--init-criteria",
        nargs="?",
        const="a11y-criteria.yaml",
        default=None,
        help="Generate a baseline editable criteria configuration file and exit",
    )
```
In `run_cli_pipeline`:
- If `--init-criteria` is supplied, generate the template via `generate_criteria_template` and exit 0.
- If `--criteria` is passed (or `.a11y-criteria.yaml` exists in cwd), load via `load_criteria_config`, pass excluded SCs to `apply_criteria_config(findings, excluded_sc)`, and pass `excluded_sc` to `render_md`.

---

### Phase 9: PySide6 Desktop GUI Criteria Filter Dialog (`engine_a11y.gui`)

#### Task 9.1: Interactive Criteria Checklist Filter in GUI
**Objective:** Add a criteria management dialog to the PySide6 desktop GUI allowing end users to visually check/uncheck criteria with checkboxes and trigger immediate "what-if" re-scoring.

**Files:**
- Test: `/Users/scott/code/local/engine-a11y/tests/test_gui_criteria_dialog.py`
- Create: `/Users/scott/code/local/engine-a11y/src/engine_a11y/gui/criteria_dialog.py`

---

### Phase 10: Downstream Integration & Parity Verification

#### Tasks 10.1 - 10.4: Connect `docx-a11y`, `pptx-a11y`, `xslx-a11y`, `pdf-a11y`
Each tool:
1. Depends on `engine-a11y`.
2. Uses its format profile (`get_docx_profile()`, etc.).
3. Supports `--criteria` and `--init-criteria`.
4. Runs what-if scenarios (e.g. `pptx-a11y deck.pptx --criteria brand-waiver.yaml`).

---

## Verification & User Story Acceptance Scenarios

1. **What-If Brand Colors Test:**
   ```bash
   # 1. Generate template
   docx-a11y --init-criteria brand-whatif.yaml

   # 2. Uncheck color contrast in the text file
   sed -i '' 's/1.4.3: true/1.4.3: false/' brand-whatif.yaml

   # 3. Audit document
   docx-a11y corporate-template.docx --criteria brand-whatif.yaml --format md

   # 4. Verify output
   # - Contrast check executed
   # - 1.4.3 findings marked [EXCLUDED FROM SUMMARY]
   # - Excluded bucket counts contrast barriers
   # - Final compliance verdict evaluates all other barriers (headings, alt text, titles)
   ```

2. **Full Conformance Matrix Transparency:**
   - Even with 1.4.3 excluded, the Conformance Matrix displays:
     `| 1.4.3 | Contrast (Minimum) | AA | [FAIL] | [EXCLUDED FROM SUMMARY] Automated check detected 3 barriers: Evaluates contrast ratio... (Excluded from compliance score via user criteria configuration) |`
