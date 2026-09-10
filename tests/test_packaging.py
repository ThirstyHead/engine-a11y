"""Tests for shared packaging infrastructure in engine-a11y."""
from pathlib import Path
from PIL import Image

from engine_a11y.packaging.icons import generate_app_icons, THEME_COLORS
from engine_a11y.packaging.specs import get_base_gui_spec_config, get_base_cli_spec_config
from engine_a11y.packaging.templates import (
    render_inno_setup_script,
    render_dmg_script,
    render_appimage_script,
    render_github_workflow,
)


def test_theme_colors_defined():
    assert "pdf" in THEME_COLORS
    assert "docx" in THEME_COLORS
    assert "pptx" in THEME_COLORS
    assert "xlsx" in THEME_COLORS


def test_generate_app_icons_creates_png_and_ico(tmp_path):
    output_dir = tmp_path / "icons"
    generated = generate_app_icons(
        app_name="test-a11y",
        bg_color=(200, 30, 30, 255),
        symbol_text="TEST",
        output_dir=output_dir,
    )
    assert "png" in generated
    assert "ico" in generated
    assert "icns" in generated
    assert generated["png"].exists()
    assert generated["ico"].exists()
    assert generated["icns"].exists()

    with Image.open(generated["png"]) as img:
        assert img.size == (256, 256)


def test_get_base_gui_spec_config():
    config = get_base_gui_spec_config(
        app_name="sample-a11y",
        entrypoint_path=Path("packaging/entrypoints/gui_main.py"),
    )
    assert "engine_a11y" in config["hiddenimports"]
    assert "tkinter" in config["excludes"]
    assert "PySide6" in config["hiddenimports"]


def test_get_base_cli_spec_config():
    config = get_base_cli_spec_config(
        app_name="sample-a11y",
        entrypoint_path=Path("packaging/entrypoints/cli_main.py"),
    )
    assert "engine_a11y" in config["hiddenimports"]
    assert "PySide6" in config["excludes"]


def test_render_inno_setup_script():
    content = render_inno_setup_script(
        app_name="sample-a11y",
        display_name="Sample Accessibility Auditor",
        version="1.0.0",
        publisher="ThirstyHead",
        exe_source_dir="dist/sample-a11y-gui",
        icon_path="packaging/icons/sample-a11y.ico",
    )
    assert 'MyAppName "sample-a11y"' in content
    assert 'MyAppDisplayName "Sample Accessibility Auditor"' in content
    assert 'MyAppVersion "1.0.0"' in content
    assert "OutputBaseFilename=sample-a11y-setup-v{#MyAppVersion}" in content


def test_render_dmg_script():
    content = render_dmg_script(
        app_name="sample-a11y",
        version="1.0.0",
        signing_identity="-",
    )
    assert 'APP_NAME="sample-a11y"' in content
    assert 'VERSION="1.0.0"' in content
    assert 'codesign --force --deep -s "${SIGN_IDENTITY}"' in content


def test_render_appimage_script():
    content = render_appimage_script(
        app_name="sample-a11y",
        version="1.0.0",
    )
    assert 'APP_NAME="sample-a11y"' in content
    assert 'VERSION="1.0.0"' in content
    assert '"${PYINSTALLER_BIN}" --noconfirm --clean' in content
    assert "APPIMAGE_EXTRACT_AND_RUN=1" in content


def test_render_github_workflow():
    content = render_github_workflow(
        app_name="sample-a11y",
        display_name="Sample Accessibility Auditor",
    )
    assert "name: Build Installers & Packages" in content
    assert "gh release upload" in content
    assert '--repo "${{ github.repository }}"' in content
