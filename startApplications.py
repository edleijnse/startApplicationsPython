# Python 3.12
import sys
import os
import shutil
import subprocess
import configparser
import shlex
import tkinter as tk
from tkinter import messagebox

# Konfiguration: Anwendungs-Liste mit plattformspezifischen Start-Befehlen
# Passen Sie die Befehle nach Bedarf an Ihre Umgebung an.
def load_apps_from_ini(path: str) -> list[dict]:
    """
    Lädt Anwendungen und plattformspezifische Befehle aus einer INI-Datei.

    Struktur der INI-Datei:
    [AppName]             ; Sektion je Anwendung, Name dient als Default-Label
    label = Optionales Label (überschreibt Sektionsnamen)
    win = Befehl für Windows (z.B. notepad oder "explorer .")
    darwin = Befehl für macOS (z.B. "open -a TextEdit")
    linux = Befehl für Linux (z.B. "gnome-calculator")

    Hinweise:
    - Argumente werden mit shlex gesplittet (Windows: posix=False, sonst True).
    - Leere oder fehlende Plattformzeilen werden ignoriert.
    """
    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    apps: list[dict] = []

    if not os.path.exists(path):
        return apps

    cfg.read(path, encoding="utf-8")

    for section in cfg.sections():
        sec = cfg[section]
        label = (sec.get("label", section) or section).strip()
        commands: dict[str, list[str]] = {}

        for plat in ("win", "darwin", "linux"):
            raw = sec.get(plat, "").strip()
            if raw:
                # Windows verwendet häufig andere Quoting-Regeln -> posix=False
                parts = shlex.split(raw, posix=(plat != "win"))
                if parts:
                    commands[plat] = parts

        if commands:
            apps.append({"label": label, "commands": commands})

    return apps


# Pfad zur INI-Datei: via ENV START_APPS_INI oder lokale Datei im selben Ordner
CONFIG_PATH = os.environ.get(
    "START_APPS_INI",
) or os.path.join(os.path.dirname(__file__), "startApplications.ini")

APPS = load_apps_from_ini(CONFIG_PATH)

# Hilfsfunktionen
def platform_key() -> str:
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"

def command_available(cmd: list[str]) -> bool:
    """
    Prüft rudimentär, ob der angegebene Befehl verfügbar ist.
    Bei Pfaden: existiert Datei? Bei Programmnamen: ist im PATH?
    Für 'open -a AppName' (macOS) wird die Verfügbarkeit nicht vorab strikt geprüft.
    """
    if not cmd:
        return False
    head = cmd[0]

    # macOS 'open' ist i.d.R. vorhanden
    if platform_key() == "darwin" and head == "open":
        return True

    # Absoluter oder relativer Pfad
    if os.path.sep in head or (os.path.altsep and os.path.altsep in head):
        return os.path.exists(head)

    # Programm im PATH?
    return shutil.which(head) is not None

def launch_command(cmd: list[str]) -> None:
    # Startet den Prozess losgelöst vom GUI
    creationflags = 0
    start_new_session = False
    if platform_key() == "win":
        # Detached Prozessgruppe (falls verfügbar)
        creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        start_new_session = True

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=start_new_session,
            creationflags=creationflags,
        )
    except FileNotFoundError:
        raise
    except Exception as ex:
        raise RuntimeError(str(ex)) from ex

def get_platform_command(app_item: dict) -> list[str] | None:
    key = platform_key()
    cmds = app_item.get("commands", {})
    cmd = cmds.get(key)
    if not cmd:
        return None
    return cmd

# GUI-Logik
class AppLauncherGUI(tk.Tk):
    def __init__(self, apps: list[dict]):
        super().__init__()
        self.title("Anwendungen starten")
        self.geometry("620x720")
        self.resizable(True, True)

        self.apps = apps
        self.filtered_indexes: list[int] = list(range(len(self.apps)))

        # Sucheingabe
        self.search_var = tk.StringVar()
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(search_frame, text="Suche:").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        search_entry.bind("<KeyRelease>", self.on_search_change)

        # Listbox + Scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.listbox = tk.Listbox(list_frame, activestyle="dotbox")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        self.start_btn = tk.Button(btn_frame, text="Starten", command=self.start_selected)
        self.start_btn.pack(side=tk.LEFT)
        self.refresh_btn = tk.Button(btn_frame, text="Verfügbarkeit prüfen", command=self.refresh_labels)
        self.refresh_btn.pack(side=tk.LEFT, padx=(6, 0))
        self.close_btn = tk.Button(btn_frame, text="Schließen", command=self.destroy)
        self.close_btn.pack(side=tk.RIGHT)

        # Events
        self.listbox.bind("<Double-1>", lambda e: self.start_selected())
        self.bind("<Return>", lambda e: self.start_selected())

        # Initiale Befüllung
        self.populate_list()

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        self.filtered_indexes = []
        for idx, app in enumerate(self.apps):
            label = app.get("label", f"App {idx+1}")
            cmd = get_platform_command(app)
            available = command_available(cmd) if cmd else False
            display = self._format_label(label, available)
            self.listbox.insert(tk.END, display)
            self.filtered_indexes.append(idx)

    def refresh_labels(self):
        # Aktualisiert die (Verfügbar/Fehlt)-Markierung
        for vis_idx, app_idx in enumerate(self.filtered_indexes):
            app = self.apps[app_idx]
            label = app.get("label", f"App {app_idx+1}")
            cmd = get_platform_command(app)
            available = command_available(cmd) if cmd else False
            display = self._format_label(label, available)
            self.listbox.delete(vis_idx)
            self.listbox.insert(vis_idx, display)

    def _format_label(self, label: str, available: bool) -> str:
        return f"{label} {'(verfügbar)' if available else '(fehlt/unklar)'}"

    def start_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie eine Anwendung aus.")
            return
        vis_idx = sel[0]
        app_idx = self.filtered_indexes[vis_idx]
        app = self.apps[app_idx]
        cmd = get_platform_command(app)

        if not cmd:
            messagebox.showerror("Fehler", f"Für diese Plattform ist kein Befehl konfiguriert.")
            return

        if not command_available(cmd):
            proceed = messagebox.askyesno(
                "Nicht gefunden",
                "Der Befehl scheint nicht verfügbar zu sein.\nTrotzdem versuchen zu starten?",
            )
            if not proceed:
                return

        try:
            launch_command(cmd)
        except FileNotFoundError:
            messagebox.showerror("Fehler", f"Konnte den Befehl nicht finden: {cmd[0]}")
        except Exception as ex:
            messagebox.showerror("Fehler", f"Start fehlgeschlagen:\n{ex}")

    def on_search_change(self, _event=None):
        term = self.search_var.get().strip().lower()
        self.listbox.delete(0, tk.END)
        self.filtered_indexes = []

        for idx, app in enumerate(self.apps):
            label = app.get("label", f"App {idx+1}")
            if term and term not in label.lower():
                continue
            cmd = get_platform_command(app)
            available = command_available(cmd) if cmd else False
            display = self._format_label(label, available)
            self.listbox.insert(tk.END, display)
            self.filtered_indexes.append(idx)

def main():
    app = AppLauncherGUI(APPS)
    app.mainloop()

if __name__ == "__main__":
    main()