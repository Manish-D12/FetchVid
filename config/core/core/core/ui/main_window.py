import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.command_builder import build_command, to_string, PRESETS
from core.runner import run
from core.format_fetcher import fetch
from config.settings import load, save

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRESET_LABELS = {
    "mp3":      "🎵 MP3 (best quality)",
    "m4a":      "🎧 M4A / AAC",
    "best":     "🎬 Best video (max res)",
    "mp4_1080": "📹 MP4 1080p",
    "mp4_720":  "🎞 MP4 720p",
    "mkv_4k":   "💠 MKV 4K",
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("yt-dlp GUI")
        self.geometry("860x620")
        self.resizable(True, True)
        self.settings = load()
        self.selected_preset = ctk.StringVar(value=self.settings.get("default_preset", "mp3"))
        self._build_ui()
        self._update_command()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="yt-dlp GUI", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 4), padx=16)
        ctk.CTkLabel(sidebar, text="command builder", text_color="gray").pack(padx=16)
        ctk.CTkLabel(sidebar, text="PRESETS", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(20, 4), padx=16, anchor="w")

        for key, label in PRESET_LABELS.items():
            ctk.CTkRadioButton(
                sidebar, text=label,
                variable=self.selected_preset, value=key,
                command=self._update_command
            ).pack(padx=16, pady=4, anchor="w")

        # --- Main area ---
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        main.grid_columnconfigure(0, weight=1)

        # URL
        ctk.CTkLabel(main, text="VIDEO URL", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=0, sticky="w")
        url_row = ctk.CTkFrame(main, fg_color="transparent")
        url_row.grid(row=1, column=0, sticky="ew", pady=(4, 12))
        url_row.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(url_row, placeholder_text="https://www.youtube.com/watch?v=...", height=38)
        self.url_entry.grid(row=0, column=0, sticky="ew")
        self.url_entry.bind("<KeyRelease>", lambda e: self._update_command())

        ctk.CTkButton(url_row, text="List Formats", width=110, command=self._list_formats).grid(row=0, column=1, padx=(8, 0))

        # Download dir
        ctk.CTkLabel(main, text="DOWNLOAD DIRECTORY", font=ctk.CTkFont(size=11), text_color="gray").grid(row=2, column=0, sticky="w")
        dir_row = ctk.CTkFrame(main, fg_color="transparent")
        dir_row.grid(row=3, column=0, sticky="ew", pady=(4, 12))
        dir_row.grid_columnconfigure(0, weight=1)

        self.dir_label = ctk.CTkEntry(dir_row, height=36)
        self.dir_label.insert(0, self.settings["download_dir"])
        self.dir_label.configure(state="disabled")
        self.dir_label.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(dir_row, text="Browse", width=80, command=self._browse_dir).grid(row=0, column=1, padx=(8, 0))

        # Command output
        ctk.CTkLabel(main, text="GENERATED COMMAND", font=ctk.CTkFont(size=11), text_color="gray").grid(row=4, column=0, sticky="w")
        self.cmd_box = ctk.CTkTextbox(main, height=80, font=ctk.CTkFont(family="Courier New", size=12))
        self.cmd_box.grid(row=5, column=0, sticky="ew", pady=(4, 8))
        self.cmd_box.configure(state="disabled")

        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.grid(row=6, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkButton(btn_row, text="Copy Command", command=self._copy_cmd).pack(side="left")
        ctk.CTkButton(btn_row, text="Run Download", fg_color="#c0392b", hover_color="#a93226", command=self._run_download).pack(side="left", padx=8)

        # Output log
        ctk.CTkLabel(main, text="OUTPUT LOG", font=ctk.CTkFont(size=11), text_color="gray").grid(row=7, column=0, sticky="w")
        self.log_box = ctk.CTkTextbox(main, height=180, font=ctk.CTkFont(family="Courier New", size=11))
        self.log_box.grid(row=8, column=0, sticky="nsew", pady=(4, 0))
        main.grid_rowconfigure(8, weight=1)

    def _update_command(self):
        url = self.url_entry.get().strip() or "YOUR_URL"
        preset = self.selected_preset.get()
        download_dir = self.settings["download_dir"]
        cmd = build_command(preset, url, download_dir)
        self.cmd_box.configure(state="normal")
        self.cmd_box.delete("1.0", "end")
        self.cmd_box.insert("1.0", to_string(cmd))
        self.cmd_box.configure(state="disabled")

    def _copy_cmd(self):
        self.clipboard_clear()
        self.clipboard_append(self.cmd_box.get("1.0", "end").strip())
        messagebox.showinfo("Copied", "Command copied to clipboard!")

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.settings["download_dir"])
        if d:
            self.settings["download_dir"] = d
            save(self.settings)
            self.dir_label.configure(state="normal")
            self.dir_label.delete(0, "end")
            self.dir_label.insert(0, d)
            self.dir_label.configure(state="disabled")
            self._update_command()

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _run_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL first.")
            return
        cmd = build_command(self.selected_preset.get(), url, self.settings["download_dir"])
        self._log(f"\n▶ Running: {to_string(cmd)}\n")
        run(cmd, on_line=lambda l: self.after(0, self._log, l),
                 on_done=lambda rc: self.after(0, self._log, f"\n✅ Done (exit {rc})" if rc == 0 else f"\n❌ Error (exit {rc})"))

    def _list_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Enter a URL first.")
            return
        self._log(f"\n🔍 Fetching formats for: {url}")
        def _fetch():
            try:
                formats = fetch(url)
                self.after(0, self._log, f"{'ID':<12} {'Ext':<8} {'Resolution':<16} {'VCodec':<12} {'ACodec'}")
                self.after(0, self._log, "-" * 60)
                for f in formats:
                    line = f"{f['id']:<12} {f['ext']:<8} {f['resolution']:<16} {f['vcodec']:<12} {f['acodec']}"
                    self.after(0, self._log, line)
            except Exception as e:
                self.after(0, self._log, f"❌ {e}")
        import threading
        threading.Thread(target=_fetch, daemon=True).start()