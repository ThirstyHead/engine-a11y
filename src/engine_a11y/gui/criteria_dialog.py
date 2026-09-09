"""Interactive WCAG Criteria Selection & What-If Testing Dialog."""
from typing import Dict, Optional, Set
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from ..profile import WCAG_CATALOG


class CriteriaChecklistDialog(QDialog):
    """Allows user to visually check/uncheck WCAG Success Criteria for what-if audits."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        initial_excluded: Optional[Set[str]] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("WCAG Criteria Selection & What-If Testing")
        self.resize(650, 500)

        self._excluded: Set[str] = set(initial_excluded or [])
        self._checkboxes: Dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)

        instructions = QLabel(
            "Check criteria to include in compliance scoring.\n"
            "Unchecked criteria will still be audited and reported, but their barriers "
            "will be captured in the 'excluded' bucket for what-if testing."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter criteria (e.g. 'contrast', '1.4.3')...")
        self.search_input.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_input)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.items_layout = QVBoxLayout(container)

        sorted_scs = sorted(WCAG_CATALOG.keys(), key=lambda x: [int(p) for p in x.split(".")])
        for sc in sorted_scs:
            meta = WCAG_CATALOG[sc]
            cb = QCheckBox(f"{sc} - {meta['title']} (Level {meta['level']})")
            cb.setChecked(sc not in self._excluded)
            self._checkboxes[sc] = cb
            self.items_layout.addWidget(cb)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _filter_items(self, query: str) -> None:
        q = query.lower().strip()
        for sc, cb in self._checkboxes.items():
            meta = WCAG_CATALOG[sc]
            match = q in sc.lower() or q in meta["title"].lower()
            cb.setVisible(match)

    def set_criterion_checked(self, sc: str, checked: bool) -> None:
        if sc in self._checkboxes:
            self._checkboxes[sc].setChecked(checked)

    def get_excluded_criteria(self) -> Set[str]:
        excluded: Set[str] = set()
        for sc, cb in self._checkboxes.items():
            if not cb.isChecked():
                excluded.add(sc)
        return excluded
