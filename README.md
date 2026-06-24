<div align="center">

# TZ-Convert

**A precise IANA timezone resolver and converter — desktop GUI, REST API, web server, and a static site that runs fully offline.**

[![Latest Version](https://img.shields.io/github/v/release/Ash1421/TZ-Convert?style=for-the-badge&label=Latest%20Version&logo=github&logoColor=white&labelColor=1c1917&color=6829B1)](https://github.com/Ash1421/TZ-Convert/releases/latest)
[![Build](https://img.shields.io/github/actions/workflow/status/Ash1421/TZ-Convert/build.yml?style=for-the-badge&logo=github-actions&logoColor=white&labelColor=1c1917&color=6829B1&label=Build)](https://github.com/Ash1421/TZ-Convert/actions/workflows/build.yml)
[![Total Downloads](https://img.shields.io/github/downloads/Ash1421/TZ-Convert/total?style=for-the-badge&logo=github&logoColor=white&labelColor=1c1917&color=6829B1&label=Total%20Downloads)](https://github.com/Ash1421/TZ-Convert/releases)
[![License: GPL v3.0](https://img.shields.io/badge/License-GPL%20v3.0-6829B1.svg?style=for-the-badge&labelColor=1c1917&logo=gnu&logoColor=white)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1c1917)](https://www.python.org/)

[![GitHub Issues](https://img.shields.io/github/issues/Ash1421/TZ-Convert/open?style=for-the-badge&labelColor=1c1917&logo=github&logoColor=white)](https://github.com/Ash1421/TZ-Convert/issues)
[![New Issue](https://img.shields.io/badge/Open%20A%20New-Issue-orange?style=for-the-badge&labelColor=1c1917&logo=github&logoColor=white)](https://github.com/Ash1421/TZ-Convert/issues/new/choose)

**Live web version — [tzc.ash1421.com](https://tzc.ash1421.com)**

</div>

---

## ✨ What's Included

🌍 **Timezone Resolver** — Maps cities, states, countries, and abbreviations to correct IANA strings, with regional edge-case handling (e.g. western Kansas → Mountain Time, Florida panhandle → Central Time)  
⏱ **Time Converter** — DST-aware conversion between any two IANA timezones  
🖥️ **Desktop GUI** — Dark purple `customtkinter` app with live world clocks  
🌐 **Static Web Page** — Works offline by cloning the repo and opening `index.html`
🔌 **Flask REST API** — Serve the app and API locally with `--server`  
💻 **CLI** — Resolve or convert directly from your terminal  
📦 **Windows EXE** — Single-file, no Python required; built automatically on release  

---

## ❤️ Made With Love Using

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1c1917)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white&labelColor=1c1917)](https://flask.palletsprojects.com/)
[![customtkinter](https://img.shields.io/badge/customtkinter-6829B1?style=for-the-badge&logo=python&logoColor=white&labelColor=1c1917)](https://github.com/TomSchimansky/CustomTkinter)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-EXE-darkred?style=for-the-badge&logo=python&logoColor=white&labelColor=1c1917)](https://pyinstaller.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white&labelColor=1c1917)](https://github.com/features/actions)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=github-pages&logoColor=white&labelColor=1c1917)](https://pages.github.com/)
[![Shields.io](https://img.shields.io/badge/Shields.io-darkgreen.svg?style=for-the-badge&logo=shields.io&logoColor=white&labelColor=1c1917)](https://shields.io/)

---

## 🌐 Web Version

The static site lives in the root of this repo (`index.html` + `assets/`). It is automatically deployed to **[tzc.ash1421.com](https://tzc.ash1421.com)** on every push to `main`.

It works fully offline too — clone the repo and open `index.html` directly in your browser. No server or build step needed.

---

## 🚀 Installation

### Option A — Download the EXE (Windows, no Python needed)

Go to the [Latest Release](https://github.com/Ash1421/TZ-Convert/releases/latest) and download `tz-convert-vX.X.X-windows-x64.exe`.

Double-click to launch the GUI.

---

### Option B — Run from source (Python 3.9+)

```bash
# 1. Clone the repo
git clone https://github.com/Ash1421/TZ-Convert.git
cd TZ-Convert

# 2. Install dependencies
# tzdata is required on Windows — it provides the timezone database
pip install -r requirements.txt

# 3. Launch (GUI by default)
python src/main.py
```

---

## 💻 Usage

### Desktop GUI

```bash
python src/main.py
python src/main.py --gui
```

Three tabs: Converter, Resolver, and World Clocks. World Clocks updates live every second.

---

### Web Server

```bash
python src/main.py --server
# Open http://127.0.0.1:5000

# Custom host and port:
python src/main.py --server --host 0.0.0.0 --port 8080
```

Serves the same static frontend as the GitHub Pages site, plus the REST API at `/api/`.

---

### CLI

```bash
# Resolve a location to its IANA timezone
python src/main.py --cli Denver
python src/main.py --cli "Goodland, KS"
python src/main.py --cli PST
python src/main.py --cli Australia
python src/main.py --cli "New Zealand"

# Convert a time between zones
python src/main.py --cli "2026-06-22 14:30" UTC "Australia/Sydney"
python src/main.py --cli "2026-06-22 09:00" "America/Denver" "Asia/Tokyo"
```

---

<details>
<summary><b>REST API Reference</b></summary>

All endpoints return JSON. Default base: `http://127.0.0.1:5000`

**`GET /api/convert`** — Convert a time

| Parameter | Required | Description |
|-----------|----------|-------------|
| `time` | yes | `YYYY-MM-DD HH:MM` |
| `from` | yes | Source IANA timezone (or alias / location) |
| `to` | yes | Target IANA timezone (or alias / location) |

```
/api/convert?time=2026-06-22+14:30&from=UTC&to=Australia/Sydney
```

**`GET /api/resolve`** — Resolve a location

```
/api/resolve?location=Denver
/api/resolve?location=Goodland%2C+KS
/api/resolve?location=Australia
```

**`GET /api/current`** — Current time in a timezone

```
/api/current?tz=America/Denver
```

**`GET /api/timezones`** — Search IANA strings

```
/api/timezones?q=australia
/api/timezones?prefix=America
```

**`GET /api/world`** — World clock snapshot

</details>

---

<details>
<summary><b>Resolution Logic</b></summary>

The resolver works through 10 priority steps:

1. Timezone alias — `PST` → `America/Los_Angeles`
2. Direct IANA string — `America/Denver` passed through validated
3. City lookup — `Denver` → `America/Denver`
4. City + region — `Goodland, KS` → `America/Denver` (western Kansas override)
5. US state — `Kansas` → `America/Chicago`
6. Country — `Australia` → `Australia/Sydney`
7. Fuzzy city match
8. Fuzzy state match
9. Fuzzy country match
10. System timezone fallback

**Multi-timezone state overrides:**

| State | Default | Override |
|-------|---------|----------|
| Kansas | `America/Chicago` | Western counties (Goodland, Liberal, Garden City…) → `America/Denver` |
| Florida | `America/New_York` | Panhandle (Pensacola, Destin…) → `America/Chicago` |
| Texas | `America/Chicago` | Far west (El Paso, Marfa…) → `America/Denver` |

</details>

---

<details>
<summary><b>Building the EXE</b></summary>

Requires Windows (or the Windows runner in CI).

```bash
pip install pyinstaller tzdata
pip install -r requirements.txt
pyinstaller tz_convert.spec --noconfirm
# Output: dist/tz-convert.exe
```
</details>

---

## 🐛 Issues & Support

- [Report a Bug](https://github.com/Ash1421/TZ-Convert/issues/new?template=bug_report.yml)
- [Request a Feature](https://github.com/Ash1421/TZ-Convert/issues/new?template=feature_request.yml)

---

## 📜 License

[GPL v3.0](./LICENSE) — GNU General Public License V3.0

---

<div align="center">

**Made with 💜 by [@Ash1421](https://github.com/Ash1421)**

⭐ **Star this repo if it helped!** ⭐

</div>
