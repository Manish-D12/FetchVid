import sys, os, shutil, threading, urllib.request
import tkinter as tk
from tkinter import ttk, messagebox


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_app_dir():
    """Directory where the exe (or script) lives."""
    if getattr(sys, "frozen", False):          # running as PyInstaller exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def find_ytdlp():
    """Return the yt-dlp command/path to use, or None if not found."""
    # 1. Check next to the exe first (our downloaded copy)
    local = os.path.join(get_app_dir(), "yt-dlp.exe")
    if os.path.isfile(local):
        return local
    # 2. Fall back to system PATH (e.g. installed via pip by the user)
    if shutil.which("yt-dlp"):
        return "yt-dlp"
    return None


# ── Download yt-dlp.exe from GitHub ──────────────────────────────────────────

YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

def _do_download(dest, on_progress, on_done):
    try:
        req = urllib.request.Request(YTDLP_URL, headers={"User-Agent": "FetchVid"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(16384)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        on_progress(downloaded / total)
        on_done(True, dest)
    except Exception as exc:
        if os.path.exists(dest):
            os.remove(dest)
        on_done(False, str(exc))


# ── First-run setup dialog ────────────────────────────────────────────────────

def show_setup_dialog():
    dest = os.path.join(get_app_dir(), "yt-dlp.exe")
    result = [None]

    root = tk.Tk()
    root.title("FetchVid — First Time Setup")
    root.geometry("420x170")
    root.resizable(False, False)
    root.configure(bg="#1c1c1c")
    root.eval("tk::PlaceWindow . center")

    tk.Label(root, text="Setting up FetchVid...",
             bg="#1c1c1c", fg="white",
             font=("Segoe UI", 13, "bold")).pack(pady=(26, 4))

    tk.Label(root, text="Downloading yt-dlp — this only happens once.",
             bg="#1c1c1c", fg="#888888",
             font=("Segoe UI", 10)).pack()

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("FV.Horizontal.TProgressbar",
                    troughcolor="#2b2b2b", background="#E63946",
                    thickness=8, borderwidth=0)

    bar = ttk.Progressbar(root, length=360, mode="determinate",
                          style="FV.Horizontal.TProgressbar")
    bar.pack(pady=16)

    status_var = tk.StringVar(value="Connecting...")
    tk.Label(root, textvariable=status_var,
             bg="#1c1c1c", fg="#666666",
             font=("Segoe UI", 9)).pack()

    def on_progress(pct):
        root.after(0, bar.configure, {"value": pct * 100})
        root.after(0, status_var.set, f"Downloading... {int(pct * 100)}%")

    def on_done(success, info):
        result[0] = success
        if success:
            root.after(0, status_var.set, "Done! Starting FetchVid...")
            root.after(900, root.destroy)
        else:
            root.after(0, status_var.set, f"Error: {info}")
            root.after(3500, root.destroy)

    threading.Thread(target=_do_download,
                     args=(dest, on_progress, on_done),
                     daemon=True).start()

    root.mainloop()
    return result[0] is True


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ytdlp = find_ytdlp()

    if ytdlp is None:
        success = show_setup_dialog()
        if not success:
            messagebox.showerror(
                "FetchVid",
                "Could not download yt-dlp.\n\n"
                "Please check your internet connection and try again."
            )
            sys.exit(1)
        ytdlp = os.path.join(get_app_dir(), "yt-dlp.exe")

    # Pass the resolved path to the rest of the app via env var
    os.environ["YTDLP_PATH"] = ytdlp

    from ui.main_window import App
    app = App()
    app.mainloop()
