# Start Applications Launcher

A small cross-platform launcher with a simple GUI to start frequently used applications or commands. It reads a configurable INI file, shows a searchable list, indicates whether each command looks available, and launches the selected entry.

## Highlights
- One INI file defines your app list with per-platform commands.
- Works on Windows, macOS, and Linux.
- Lightweight: standard Python only (no third‑party dependencies).
- Simple GUI with search, double-click/Enter to launch, and availability refresh.

## Requirements
- Python 3.12+
- Tk (tkinter) available on your system
  - Windows/macOS: usually included with Python installers
  - Linux: you may need to install your distribution’s Tk package (e.g., `python3-tk`)

## Quick Start
1. Create your INI file (for example: `startAppications.ini`).
2. Launch the app:
   - EITHER set the environment variable `START_APPS_INI` to point to your INI file and run the script
   - OR place your INI file next to the script and run the script

Example command:
- Windows (PowerShell): `$env:START_APPS_INI="C:\path\to\startAppications.ini"; python path\to\startApplications.py`
- macOS/Linux (bash/zsh): `START_APPS_INI="/path/to/startAppications.ini" python /path/to/startApplications.py`

Tip: If you do not set `START_APPS_INI`, the script looks for an INI file in the same directory as the script. Use the environment variable when your file name or location differs.

## INI File Format
Define one section per app. Each section can include:
- `label`: Optional display name (defaults to the section name if omitted)
- `win`: Command to run on Windows
- `darwin`: Command to run on macOS
- `linux`: Command to run on Linux

Example (`startAppications.ini`):
