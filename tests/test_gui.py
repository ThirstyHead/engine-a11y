import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from engine_a11y.gui.models import BatchItem
from engine_a11y.gui.theme import APP_STYLESHEET
from engine_a11y.gui.criteria_dialog import CriteriaChecklistDialog
from engine_a11y.gui.triage_dialog import TriageDialog
from engine_a11y.triage import TriageSession

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_batch_item_model():
    item = BatchItem(path=Path("/tmp/sample.docx"))
    assert item.status == "Pending"
    assert item.score == 0.0
    assert item.findings_count == 0

def test_theme_stylesheet():
    assert "QMainWindow" in APP_STYLESHEET
    assert "QPushButton#btn_primary" in APP_STYLESHEET

def test_criteria_dialog(qapp):
    dialog = CriteriaChecklistDialog(initial_excluded={"1.4.3"})
    assert dialog.windowTitle() == "WCAG Criteria Selection & What-If Testing"
    excluded = dialog.get_excluded_criteria()
    assert "1.4.3" in excluded

    # Toggle 1.4.3 back to included
    dialog.set_criterion_checked("1.4.3", True)
    assert "1.4.3" not in dialog.get_excluded_criteria()

def test_triage_dialog(qapp):
    findings = [
        {"rule_id": "title-missing", "location": "doc", "message": "Document title is missing."}
    ]
    session = TriageSession(findings)
    dialog = TriageDialog(session=session)
    assert dialog.windowTitle() == "Accessibility Remediation Triage"
    assert len(dialog.field_inputs) == 1


def test_theme_story_elements():
    assert "#pane_before" in APP_STYLESHEET
    assert "#pane_after" in APP_STYLESHEET
    assert "#center_bridge" in APP_STYLESHEET
    assert "#btn_remediate_primary" in APP_STYLESHEET
    assert "#guide_banner" in APP_STYLESHEET


def test_report_viewer_dialog(qapp, tmp_path: Path):
    from engine_a11y.gui import ReportViewerDialog

    report_file = tmp_path / "test-report.md"
    report_file.write_text("# Accessibility Audit Report\nScore: 95%\n", encoding="utf-8")

    dialog = ReportViewerDialog(report_path=report_file, score=95.0)
    assert "test-report.md" in dialog.windowTitle()
    assert dialog.browser is not None
    assert "95%" in dialog.browser.toPlainText()
    assert "GOOD" in dialog.lbl_score_badge.text()
    assert dialog.lbl_score_badge.property("severity") == "pass"
    assert dialog.btn_open_external is not None
    assert dialog.btn_open_folder is not None

