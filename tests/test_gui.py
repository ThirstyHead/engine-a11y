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
