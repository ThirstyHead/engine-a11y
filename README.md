# engine-a11y

Core accessibility engine, data models, contrast algorithms, reporting, triage, desktop GUI, and packaging infrastructure shared across format-specific document accessibility tools (`pdf-a11y`, `docx-a11y`, `pptx-a11y`, `xlsx-a11y`).

---

## Features

- **Standardized Findings & Immutability**: Uniform data structures (`Finding`, `Severity`), non-destructive source protection, and SHA-256 verification.
- **Criteria Modeling & What-If Analysis**: Text-based checklist and YAML criteria configurations (`a11y-criteria.yaml`) partitioning unchecked findings into non-blocking excluded buckets.
- **WCAG Catalog & Contrast Math**: Canonical Level A/AA criteria matrix, relative luminance calculations, and deterministic contrast adjustment algorithms.
- **Multi-Format Report Generation**: Full SC coverage matrices across Markdown, standalone HTML5, and tagged PDF reports.
- **Interactive Triage & Desktop GUI**: PySide6/Qt workflow widgets, triage dialogs, and background inspection workers.
- **Cross-Platform Packaging Infrastructure**: Shared icon generation (`.png`, `.ico`, `.icns`), PyInstaller spec helpers (preventing binary collisions between GUI and CLI entrypoints), Inno Setup templates, DMG/AppImage scripts, and GitHub Actions packaging workflows.

---

## Shared Packaging Infrastructure (`engine_a11y.packaging`)

Format-specific auditor repositories inherit uniform packaging logic from `engine_a11y.packaging`:

```python
from engine_a11y.packaging.icons import generate_app_icons, THEME_COLORS
from engine_a11y.packaging.specs import get_base_gui_spec_config, get_base_cli_spec_config
from engine_a11y.packaging.templates import (
    render_inno_setup_script,
    render_dmg_script,
    render_appimage_script,
    render_github_workflow,
)

# 1. Generate multi-resolution icons (.png, .ico, .icns)
generate_app_icons("docx-a11y", THEME_COLORS["docx"], symbol_text="DOCX")

# 2. Get PyInstaller configuration helpers
gui_config = get_base_gui_spec_config("docx-a11y", Path("packaging/entrypoints/gui_main.py"))
cli_config = get_base_cli_spec_config("docx-a11y", Path("packaging/entrypoints/cli_main.py"))

# 3. Render standardized installer scripts
inno_script = render_inno_setup_script("docx-a11y", "Word Accessibility Auditor", "0.5.0")
dmg_script = render_dmg_script("docx-a11y", "0.5.0")
appimage_script = render_appimage_script("docx-a11y", "0.5.0")
workflow = render_github_workflow("docx-a11y", "Word Accessibility Auditor")
```

---

## Development & Testing

```bash
uv pip install -e ".[all]"
pytest
```
