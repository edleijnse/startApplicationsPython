# startApplicationsPython
A lightweight, cross-platform Python launcher with a simple Tkinter GUI to quickly start commonly used applications from a configurable list. Works on Windows, macOS, and Linux.
## Features
- Clean GUI with search and a scrollable list
- Platform-specific launch commands (Windows/macOS/Linux)
- Per-item availability indicator (available vs. missing/unknown)
- Start via double-click or Enter
- “Re-check availability” button
- Launches processes detached from the GUI

## Requirements
- Python 3.12
- Tkinter runtime:
    - Windows/macOS: usually included with Python
    - Linux: install your distribution’s Tk package (for example, “python3-tk”)

- The applications you want to launch must be installed and either in PATH or referenced by a valid absolute path
- Project uses virtualenv as the Python environment manager

## Installation
1. Get the project folder on your machine.
2. Create and activate a virtual environment:
``` bash
# Bash (Linux/macOS)
python3 -m virtualenv .venv
source .venv/bin/activate
```

``` powershell
# PowerShell (Windows)
py -3.12 -m virtualenv .venv
.\.venv\Scripts\Activate.ps1
```
1. Install dependencies:

- No additional PyPI packages are required.

## Run
Activate the virtual environment (if not already active) and start the app:
``` bash
# Linux/macOS
python startApplications.py
```

``` powershell
# Windows
py -3.12 startApplications.py
```
The GUI will open with a predefined list of applications.
## Usage
- Search: Type in the search field to filter the list.
- Start: Double-click an entry or press Enter.
- Check availability: Use the “Re-check availability” button to refresh indicators.
- Close: Use the “Close” button.

If a command cannot be found, you can still attempt to launch or adjust the configuration first.
## Configuration
The application list is defined in the script. Each entry includes:
- label: Display name
- commands: A mapping for “win” (Windows), “darwin” (macOS), and “linux”

Tips:
- Prefer program names available in PATH (e.g., “notepad”, “calc”, “gnome-calculator”) or use absolute paths.
- macOS: “open -a AppName” launches apps by name.
- Linux: Terminal/editors may vary by desktop environment (e.g., “x-terminal-emulator”, “gnome-terminal”, “konsole”).
- Windows: Built-in tools like “notepad”, “calc”, and “explorer” typically work without extra setup.

Restart the app after making changes.
## Platform Notes
- Windows:
    - Built-in utilities run out of the box.
    - If some apps require elevation, start your Python session accordingly.

- macOS:
    - Many apps can be started via “open -a ”.
    - Availability checks for “open -a …” are not strict; launching still works.

- Linux:
    - Ensure Tk is installed (e.g., package “python3-tk”).
    - Desktop environments differ; adjust commands to your setup.
    - “xdg-open .” is useful for opening folders with your default file manager.

## Troubleshooting
- Command not found:
    - Check if the program is in PATH (e.g., “which ” on Linux/macOS or “where ” on Windows).
    - Alternatively, use an absolute path.

- GUI does not start:
    - Verify Python 3.12.
    - On Linux, ensure “python3-tk” is installed.

- Program starts and exits immediately:
    - Some commands may represent non-GUI tools or require additional parameters; use an alternative launcher/command.

## Development
- Language: Python 3.12
- GUI: Tkinter (standard library)
- Recommended workflow:
    - Use virtualenv
    - Customize the application list in the script
    - Test on each target platform

## License
Add your license information here (e.g., MIT, Apache-2.0).
