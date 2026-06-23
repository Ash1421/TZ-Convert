# tz_convert.spec — PyInstaller build spec
# Produces a single-file Windows EXE with no console window.
#
# Build manually:
#   pip install pyinstaller tzdata
#   pyinstaller tz_convert.spec --noconfirm
#
# Or push a git tag (v*) to trigger the GitHub Actions build.

from pathlib import Path

block_cipher = None
src = str(Path("src").resolve())

a = Analysis(
    [str(Path("src") / "main.py")],
    pathex=[src],
    binaries=[],
    datas=[
        # Bundle the static web files so --server mode works from the EXE
        ("index.html",  "."),
        ("assets",      "assets"),
    ],
    hiddenimports=[
        "zoneinfo",
        "zoneinfo._tzpath",
        "tzdata",
        "customtkinter",
        "flask",
        "werkzeug",
        "click",
        "jinja2",
        "itsdangerous",
        "darkdetect",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="tz-convert",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # No console window — GUI is default
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/img/icon.ico",
)
