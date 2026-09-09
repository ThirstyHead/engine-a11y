"""Interactive GUI Triage Dialog for author-intent accessibility decisions."""
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from ..triage import TriageSession


class TriageDialog(QDialog):
    """Presents pending author-intent triage items for human resolution in GUI."""

    def __init__(self, session: TriageSession, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Accessibility Remediation Triage")
        self.resize(700, 500)

        self.field_inputs: Dict[int, QWidget] = {}
        layout = QVBoxLayout(self)

        header = QLabel(
            "Review and resolve author-intent accessibility items.\n"
            "Provide appropriate alternative text, document titles, or language codes below:"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        form_layout = QFormLayout(container)

        for idx, item in enumerate(self.session.items):
            label_text = f"<b>{item.rule_id}</b> ({item.location}):<br>{item.description}"
            lbl = QLabel(label_text)
            lbl.setWordWrap(True)

            if item.action == "boolean" and item.choices:
                combo = QComboBox()
                combo.addItems(item.choices)
                form_layout.addRow(lbl, combo)
                self.field_inputs[idx] = combo
            else:
                line_edit = QLineEdit()
                if item.current_value:
                    line_edit.setText(str(item.current_value))
                line_edit.setPlaceholderText(item.prompt)
                form_layout.addRow(lbl, line_edit)
                self.field_inputs[idx] = line_edit

        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        for idx, widget in self.field_inputs.items():
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    self.session.resolve_item(idx, text)
            elif isinstance(widget, QComboBox):
                val = widget.currentText()
                self.session.resolve_item(idx, val)
        self.accept()
