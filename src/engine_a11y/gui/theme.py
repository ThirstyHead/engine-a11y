"""Accessible Qt stylesheet and color tokens for accessibility GUI."""

APP_STYLESHEET = """
QMainWindow {
    background-color: #f8fafc;
}

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px;
    spacing: 8px;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    color: #0f172a;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton:disabled {
    background-color: #f8fafc;
    border-color: #e2e8f0;
    color: #94a3b8;
}

QPushButton#btn_primary {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#btn_primary:hover {
    background-color: #1d4ed8;
}

QPushButton#btn_primary:disabled {
    background-color: #93c5fd;
    border-color: #93c5fd;
    color: #ffffff;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    gridline-color: #f1f5f9;
    selection-background-color: #eff6ff;
    selection-color: #1e3a8a;
}

QHeaderView::section {
    background-color: #f8fafc;
    border: none;
    border-bottom: 1px solid #cbd5e1;
    padding: 6px 8px;
    font-weight: 600;
    color: #334155;
}

QGroupBox {
    font-weight: 600;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
    color: #1e293b;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    text-align: center;
    background-color: #e2e8f0;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}

/* Before & After Storytelling Panels */
QGroupBox#pane_before, QGroupBox#pane_after {
    font-size: 13px;
    font-weight: bold;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin-top: 12px;
    background-color: #ffffff;
}

QGroupBox#pane_before::title, QGroupBox#pane_after::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    color: #1e293b;
}

#pane_subtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: normal;
}

/* Center Remediation Bridge */
QFrame#center_bridge {
    background-color: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
}

#btn_remediate_primary {
    background-color: #2563eb;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 16px;
    border-radius: 6px;
    border: none;
}
#btn_remediate_primary:hover {
    background-color: #1d4ed8;
}
#btn_remediate_primary:disabled {
    background-color: #94a3b8;
}

/* Guide Header */
#guide_banner {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 12px;
    color: #1e40af;
    font-weight: 500;
}
"""
