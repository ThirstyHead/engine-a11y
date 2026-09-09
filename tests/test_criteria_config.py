import pytest
from pathlib import Path
from engine_a11y.criteria_config import (
    load_criteria_config,
    apply_criteria_config,
    generate_criteria_template,
)
from engine_a11y.findings import Finding

def test_load_text_checklist_format(tmp_path):
    txt_file = tmp_path / "criteria.txt"
    txt_file.write_text("""# WCAG Accessibility Criteria Checklist
# Uncheck any criterion with [ ] to audit it but exclude it from summary blocking totals.

[x] 1.1.1 Non-text Content (Level A)
[X] 1.3.1 Info and Relationships (Level A)
[ ] 1.4.3 Contrast (Minimum) (Level AA) - Brand colors in flux
[ ] 2.4.4 Link Purpose (In Context) (Level A)
[x] 2.4.2 Page Titled (Level A)
""")
    included, excluded = load_criteria_config(txt_file)
    assert "1.1.1" in included
    assert "1.3.1" in included
    assert "2.4.2" in included
    assert "1.4.3" in excluded
    assert "2.4.4" in excluded

def test_load_yaml_criteria_config(tmp_path):
    cfg_file = tmp_path / "a11y-criteria.yaml"
    cfg_file.write_text("""
criteria:
  1.1.1: true
  1.3.1: true
  1.4.3: false
  2.4.2: enable
  2.4.4: disable
""")
    included, excluded = load_criteria_config(cfg_file)
    assert "1.1.1" in included
    assert "1.3.1" in included
    assert "2.4.2" in included
    assert "1.4.3" in excluded
    assert "2.4.4" in excluded

def test_apply_criteria_config():
    f1 = Finding("image-alt-missing", "1.1.1", "critical", "loc1", "desc")
    f2 = Finding("contrast-low", "1.4.3", "serious", "loc2", "desc")
    findings = [f1, f2]

    apply_criteria_config(findings, excluded_sc={"1.4.3"})
    assert f1.excluded is False
    assert f2.excluded is True

def test_generate_criteria_template_checklist(tmp_path):
    out_file = tmp_path / "criteria.txt"
    generate_criteria_template(out_file)
    assert out_file.exists()
    content = out_file.read_text()
    assert "[x] 1.1.1 Non-text Content" in content
    assert "[x] 1.4.3 Contrast (Minimum)" in content
    assert "Uncheck any criterion with [ ]" in content

    # Verify that the generated template can be parsed immediately
    included, excluded = load_criteria_config(out_file)
    assert "1.1.1" in included
    assert "1.4.3" in included
    assert len(excluded) == 0
