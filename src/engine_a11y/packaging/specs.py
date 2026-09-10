"""Shared PyInstaller spec helper configurations for GUI and CLI targets."""
from pathlib import Path
from typing import Any, Dict, List, Optional


COMMON_EXCLUDES = [
    "tkinter",
    "unittest",
    "test",
    "tests",
    "matplotlib",
    "scipy",
    "numpy.tests",
    "IPython",
    "notebook",
]

COMMON_HIDDEN_IMPORTS = [
    "engine_a11y",
    "engine_a11y.criteria_config",
    "engine_a11y.findings",
    "engine_a11y.profile",
    "engine_a11y.contrast",
    "engine_a11y.enrich",
    "engine_a11y.immutability",
    "engine_a11y.triage",
    "engine_a11y.reports.meta",
    "engine_a11y.reports.tone",
    "engine_a11y.reports.stats",
    "engine_a11y.reports.theme",
    "engine_a11y.reports.md",
    "engine_a11y.reports.html",
    "engine_a11y.reports.pdf",
    "markdown",
    "yaml",
    "PIL",
]


def get_base_gui_spec_config(
    app_name: str,
    entrypoint_path: Path,
    icon_path: Optional[Path] = None,
    extra_hidden_imports: Optional[List[str]] = None,
    extra_excludes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Return recommended Analysis and bundle configuration for desktop GUI."""
    hidden = list(COMMON_HIDDEN_IMPORTS) + [
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "engine_a11y.gui.app",
        "engine_a11y.gui.main_window",
        "engine_a11y.gui.models",
        "engine_a11y.gui.worker",
        "engine_a11y.gui.theme",
        "engine_a11y.gui.triage_dialog",
    ]
    if extra_hidden_imports:
        hidden.extend(extra_hidden_imports)

    excludes = list(COMMON_EXCLUDES)
    if extra_excludes:
        excludes.extend(extra_excludes)

    return {
        "app_name": app_name,
        "entrypoint": str(entrypoint_path),
        "icon": str(icon_path) if icon_path else None,
        "hiddenimports": sorted(list(set(hidden))),
        "excludes": sorted(list(set(excludes))),
        "windowed": True,
    }


def get_base_cli_spec_config(
    app_name: str,
    entrypoint_path: Path,
    extra_hidden_imports: Optional[List[str]] = None,
    extra_excludes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Return recommended Analysis and binary configuration for standalone CLI."""
    hidden = list(COMMON_HIDDEN_IMPORTS) + [
        "engine_a11y.cli",
    ]
    if extra_hidden_imports:
        hidden.extend(extra_hidden_imports)

    excludes = list(COMMON_EXCLUDES) + [
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "engine_a11y.gui",
    ]
    if extra_excludes:
        excludes.extend(extra_excludes)

    return {
        "app_name": app_name,
        "entrypoint": str(entrypoint_path),
        "hiddenimports": sorted(list(set(hidden))),
        "excludes": sorted(list(set(excludes))),
        "console": True,
    }
