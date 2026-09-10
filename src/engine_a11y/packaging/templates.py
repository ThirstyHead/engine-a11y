"""Templates for multi-platform build scripts, Inno Setup, and GitHub Actions."""

def render_inno_setup_script(
    app_name: str,
    display_name: str,
    version: str,
    publisher: str = "ThirstyHead",
    exe_source_dir: str = "",
    icon_path: str = "",
) -> str:
    """Render Windows Inno Setup 6 compiler configuration."""
    if not exe_source_dir:
        exe_source_dir = f"dist/{app_name}-gui"
    if not icon_path:
        icon_path = f"packaging/icons/{app_name}.ico"

    return f"""; Inno Setup Script for {app_name} Desktop GUI Installer
#define MyAppName "{app_name}"
#define MyAppDisplayName "{display_name}"
#define MyAppVersion "{version}"
#define MyAppPublisher "{publisher}"
#define MyAppExeName "{app_name}.exe"

[Setup]
AppId={{{{{{MyAppName}}-A11Y-AUDITOR-SETUP}}}}
AppName={{#MyAppDisplayName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppDisplayName}}
DefaultGroupName={{#MyAppDisplayName}}
OutputDir=..\\..\\dist\\windows
OutputBaseFilename={app_name}-setup-v{{#MyAppVersion}}
SetupIconFile=..\\..\\{icon_path}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "..\\..\\{exe_source_dir}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\{{#MyAppDisplayName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppDisplayName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppDisplayName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
"""


def render_dmg_script(
    app_name: str,
    version: str,
    signing_identity: str = "-",
) -> str:
    """Render macOS DMG build script."""
    return f"""#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
REPO_ROOT="$(cd "${{SCRIPT_DIR}}/../.." && pwd)"

cd "${{REPO_ROOT}}"

APP_NAME="{app_name}"
VERSION="{version}"
DIST_DIR="${{REPO_ROOT}}/dist"
OUT_DIR="${{DIST_DIR}}/macos"
DMG_PATH="${{OUT_DIR}}/${{APP_NAME}}-v${{VERSION}}-macos.dmg"
APP_BUNDLE="${{DIST_DIR}}/${{APP_NAME}}.app"

mkdir -p "${{OUT_DIR}}"
rm -f "${{DMG_PATH}}"

echo "==> Building macOS .app bundle via PyInstaller..."
PYINSTALLER_BIN="${{REPO_ROOT}}/.venv/bin/pyinstaller"
if [ ! -x "${{PYINSTALLER_BIN}}" ]; then
  PYINSTALLER_BIN="$(command -v pyinstaller || true)"
fi
if [ -z "${{PYINSTALLER_BIN}}" ]; then
  echo "Error: pyinstaller executable not found."
  exit 1
fi

"${{PYINSTALLER_BIN}}" --noconfirm --clean "${{REPO_ROOT}}/packaging/specs/${{APP_NAME}}-gui.spec"

if [ ! -d "${{APP_BUNDLE}}" ]; then
  echo "Error: App bundle ${{APP_BUNDLE}} was not generated."
  exit 1
fi

# Ad-hoc codesign the .app bundle recursively
SIGN_IDENTITY="{signing_identity}"
echo "==> Applying recursive ad-hoc code signature (${{SIGN_IDENTITY}})..."
codesign --force --deep -s "${{SIGN_IDENTITY}}" "${{APP_BUNDLE}}"
codesign --verify --deep --strict --verbose=2 "${{APP_BUNDLE}}" || true

echo "==> Packaging ${{APP_BUNDLE}} into DMG..."
if command -v create-dmg >/dev/null 2>&1; then
  create-dmg \\
    --volname "${{APP_NAME}} ${{VERSION}}" \\
    --window-pos 200 120 \\
    --window-size 600 400 \\
    --icon-size 100 \\
    --icon "${{APP_NAME}}.app" 175 190 \\
    --app-drop-link 425 190 \\
    --no-internet-enable \\
    "${{DMG_PATH}}" \\
    "${{APP_BUNDLE}}" || true
fi

if [ ! -f "${{DMG_PATH}}" ]; then
  echo "==> Using hdiutil fallback to create DMG..."
  hdiutil create -volname "${{APP_NAME}} ${{VERSION}}" -srcfolder "${{APP_BUNDLE}}" -ov -format UDZO "${{DMG_PATH}}"
fi

echo "==> Ad-hoc signing the DMG image..."
codesign --force -s "${{SIGN_IDENTITY}}" "${{DMG_PATH}}" || true

echo "==> Built DMG: ${{DMG_PATH}}"
"""


def render_appimage_script(
    app_name: str,
    version: str,
) -> str:
    """Render Linux AppImage packaging script."""
    return f"""#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
REPO_ROOT="$(cd "${{SCRIPT_DIR}}/../.." && pwd)"

APP_NAME="{app_name}"
VERSION="{version}"
DIST_DIR="${{REPO_ROOT}}/dist"
APP_DIR="${{DIST_DIR}}/AppDir"
OUT_DIR="${{DIST_DIR}}/linux"

mkdir -p "${{OUT_DIR}}"
rm -rf "${{APP_DIR}}"
mkdir -p "${{APP_DIR}}/usr/bin" \\
         "${{APP_DIR}}/usr/share/applications" \\
         "${{APP_DIR}}/usr/share/icons/hicolor/256x256/apps" \\
         "${{APP_DIR}}/usr/lib"

echo "==> Building PyInstaller bundle..."
PYINSTALLER_BIN="${{REPO_ROOT}}/.venv/bin/pyinstaller"
if [ ! -x "${{PYINSTALLER_BIN}}" ]; then
  PYINSTALLER_BIN="$(command -v pyinstaller || true)"
fi
if [ -z "${{PYINSTALLER_BIN}}" ]; then
  echo "Error: pyinstaller executable not found."
  exit 1
fi

"${{PYINSTALLER_BIN}}" --noconfirm --clean "${{REPO_ROOT}}/packaging/specs/${{APP_NAME}}-gui.spec"

echo "==> Staging Linux AppDir files..."
cp -r "${{DIST_DIR}}/{app_name}-gui"/* "${{APP_DIR}}/usr/bin/"

# Ensure main launcher AppRun script
cat << EOF > "${{APP_DIR}}/AppRun"
#!/bin/sh
SELF=\\$(readlink -f "\\$0")
HERE=\\${{SELF%/*}}
export PATH="\\${{HERE}}/usr/bin:\\${{PATH}}"
export LD_LIBRARY_PATH="\\${{HERE}}/usr/bin:\\${{LD_LIBRARY_PATH:-}}"
exec "\\${{HERE}}/usr/bin/${{APP_NAME}}" "\\$@"
EOF
chmod +x "${{APP_DIR}}/AppRun"

# Copy icons
cp "${{REPO_ROOT}}/packaging/icons/{app_name}.png" "${{APP_DIR}}/usr/share/icons/hicolor/256x256/apps/"
cp "${{REPO_ROOT}}/packaging/icons/{app_name}.png" "${{APP_DIR}}/"

# Desktop entry
cat > "${{APP_DIR}}/{app_name}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name={app_name}
Exec={app_name}
Icon={app_name}
Categories=Utility;
Terminal=false
EOF

echo "==> Generating AppImage via appimagetool..."
export APPIMAGE_EXTRACT_AND_RUN=1
appimagetool "${{APP_DIR}}" "${{OUT_DIR}}/{app_name}-v${{VERSION}}-x86_64.AppImage"
echo "==> Built AppImage: ${{OUT_DIR}}/{app_name}-v${{VERSION}}-x86_64.AppImage"
"""


def render_github_workflow(
    app_name: str,
    display_name: str,
    python_version: str = "3.12",
) -> str:
    """Render multi-platform GitHub Actions packaging workflow."""
    return f"""name: Build Installers & Packages

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      release_tag:
        description: 'Target GitHub Release tag to attach assets to (e.g. v0.1.0)'
        required: false
        default: ''

jobs:
  build-macos:
    name: Build macOS DMG & CLI
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[all]" pyinstaller pillow

      - name: Generate High-Res Icons
        run: python packaging/scripts/generate_icons.py

      - name: Build Desktop GUI DMG
        run: ./packaging/macos/build_dmg.sh

      - name: Build Headless CLI Binary
        run: pyinstaller --noconfirm packaging/specs/{app_name}-cli.spec

      - name: Rename CLI binary for release
        run: |
          mv dist/{app_name} dist/{app_name}-cli-macos-arm64
          chmod +x dist/{app_name}-cli-macos-arm64

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: macos-installers
          path: |
            dist/macos/*.dmg
            dist/{app_name}-cli-macos-arm64

  build-windows:
    name: Build Windows Installer & CLI
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'

      - name: Install Inno Setup
        run: choco install innosetup -y

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[all]" pyinstaller pillow

      - name: Generate High-Res Icons
        run: python packaging/scripts/generate_icons.py

      - name: Build Desktop GUI Directory Bundle
        run: pyinstaller --noconfirm --clean packaging/specs/{app_name}-gui.spec

      - name: Compile Inno Setup Installer
        run: |
          & "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" packaging/windows/{app_name}.iss

      - name: Build Headless CLI Binary
        run: pyinstaller --noconfirm packaging/specs/{app_name}-cli.spec

      - name: Rename CLI binary for release
        run: |
          Move-Item -Path "dist\\{app_name}.exe" -Destination "dist\\{app_name}-cli-windows-x86_64.exe"

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: windows-installers
          path: |
            dist/windows/*.exe
            dist/{app_name}-cli-windows-x86_64.exe

  build-linux:
    name: Build Linux AppImage & CLI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libxcb-cursor0 libxkbcommon-x11-0 libegl1-mesa

      - name: Download appimagetool
        run: |
          sudo wget -O /usr/local/bin/appimagetool https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
          sudo chmod +x /usr/local/bin/appimagetool

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[all]" pyinstaller pillow

      - name: Generate High-Res Icons
        run: python packaging/scripts/generate_icons.py

      - name: Build Desktop GUI AppImage
        run: ./packaging/linux/build_appimage.sh

      - name: Build Headless CLI Binary
        run: pyinstaller --noconfirm packaging/specs/{app_name}-cli.spec

      - name: Rename CLI binary for release
        run: |
          mv dist/{app_name} dist/{app_name}-cli-linux-x86_64
          chmod +x dist/{app_name}-cli-linux-x86_64

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: linux-installers
          path: |
            dist/linux/*.AppImage
            dist/{app_name}-cli-linux-x86_64

  release:
    name: Publish Release Assets
    needs: [build-macos, build-windows, build-linux]
    if: startsWith(github.ref, 'refs/tags/v') || (github.event_name == 'workflow_dispatch' && inputs.release_tag != '')
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Download all workflow artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Flatten and Publish to GitHub Release
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          TARGET_TAG="${{{{ github.ref_name }}}}"
          if [ "${{{{ github.event_name }}}}" = "workflow_dispatch" ] && [ -n "${{{{ inputs.release_tag }}}}" ]; then
            TARGET_TAG="${{{{ inputs.release_tag }}}}"
          fi
          echo "Publishing release assets to ${{TARGET_TAG}}..."
          mkdir -p release-assets
          find artifacts -type f -exec cp {{}} release-assets/ \\;
          gh release upload "${{TARGET_TAG}}" release-assets/* --clobber --repo "${{{{ github.repository }}}}"
"""
