import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.command_builder import build_command, to_string
from core.runner import run
from config.settings import load, save

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRESETS_INFO = {
    "mp3":      {"label": "MP3",       "sub": "Best quality", "icon": "🎵"},
    "m4a":      {"label": "M4A",       "sub": "Apple / AAC",  "icon": "🎧"},
    "mp4_720":  {"label": "MP4 720p",  "sub": "HD video",     "icon": "📹"},
    "mp4_1080": {"label": "MP4 1080p", "sub": "Full HD",      "icon": "🎬"},
    "mkv_4k":   {"label": "MKV 4K",   "sub": "Max quality",  "icon": "💠"},
    "best":     {"label": "Best",      "sub": "Auto select",  "icon": "⚡"},
}

ACCENT = "#E63946"
ACCENT_HOVER = "#c1121f"
CARD_NORMAL = "#2b2b2b"
BG_MAIN = "#1c1c1c"
BG_DARK = "#141414"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FetchVid")
        self.geometry("700x820")
        self.resizable(True, True)
        self.settings = load()
        self.selected_preset = "mp3"
        self.preset_buttons = {}
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Main container ──────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        main.grid(row=0, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # ── Header ───────────────────────────────────────────────
        header = ctk.CTkFrame(main, fg_color=BG_DARK, corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Canvas logo — play triangle + download arrow
        c = ctk.CTkCanvas(logo_frame, width=40, height=40,
                          bg=BG_DARK, highlightthickness=0)
        c.pack(side="left", padx=(0, 10))
        # Play triangle
        c.create_polygon(4, 2, 4, 38, 38, 20, fill=ACCENT, outline="")
        # Arrow stem
        c.create_rectangle(16, 10, 22, 24, fill="white", outline="")
        # Arrow head
        c.create_polygon(11, 22, 27, 22, 19, 32, fill="white", outline="")

        ctk.CTkLabel(
            logo_frame, text="FetchVid",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(side="left")

        # ── Content ───────────────────────────────────────────────
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=32, pady=20)
        content.grid_columnconfigure(0, weight=1)

        # URL
        ctk.CTkLabel(
            content, text="VIDEO URL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#666666"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.url_entry = ctk.CTkEntry(
            content,
            placeholder_text="Paste YouTube or video URL here...",
            height=44, font=ctk.CTkFont(size=13),
            fg_color="#2b2b2b", border_color="#3a3a3a",
            border_width=1, corner_radius=8
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Format
        ctk.CTkLabel(
            content, text="FORMAT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#666666"
        ).grid(row=2, column=0, sticky="w", pady=(0, 8))

        cards_frame = ctk.CTkFrame(content, fg_color="transparent")
        cards_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)

        for idx, (key, info) in enumerate(PRESETS_INFO.items()):
            self._make_card(cards_frame, key, info, idx // 3, idx % 3)

        # Save to
        ctk.CTkLabel(
            content, text="SAVE TO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#666666"
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        dir_row = ctk.CTkFrame(content, fg_color="transparent")
        dir_row.grid(row=5, column=0, sticky="ew", pady=(0, 28))
        dir_row.grid_columnconfigure(0, weight=1)

        self.dir_label = ctk.CTkEntry(
            dir_row, height=38, font=ctk.CTkFont(size=12),
            fg_color="#2b2b2b", border_color="#3a3a3a",
            border_width=1, corner_radius=8
        )
        self.dir_label.insert(0, self.settings["download_dir"])
        self.dir_label.configure(state="disabled")
        self.dir_label.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            dir_row, text="Browse", width=90, height=38,
            fg_color="#2b2b2b", hover_color="#3a3a3a",
            border_color="#3a3a3a", border_width=1,
            corner_radius=8, command=self._browse_dir
        ).grid(row=0, column=1, padx=(8, 0))

        # Download button
        ctk.CTkButton(
            content, text="⬇   Download Now",
            height=52, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=10, command=self._run_download
        ).grid(row=6, column=0, sticky="ew", pady=(0, 16))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            content, height=6, corner_radius=3,
            fg_color="#2b2b2b", progress_color=ACCENT
        )
        self.progress.set(0)
        self.progress.grid(row=7, column=0, sticky="ew", pady=(0, 8))

        # Status
        self.status_label = ctk.CTkLabel(
            content, text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        self.status_label.grid(row=8, column=0, sticky="w", pady=(0, 8))

        # Log
        self.log_box = ctk.CTkTextbox(
            content, height=80,
            font=ctk.CTkFont(family="Courier New", size=10),
            fg_color=BG_DARK, border_color="#2b2b2b",
            border_width=1, corner_radius=8,
            text_color="#888888"
        )
        self.log_box.grid(row=9, column=0, sticky="ew")

        # ── Footer ────────────────────────────────────────────────
        footer = ctk.CTkFrame(main, fg_color=BG_DARK, corner_radius=0, height=28)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)

        ctk.CTkLabel(
            footer, text="by shrek  🟢",
            font=ctk.CTkFont(size=11),
            text_color="#444444"
        ).place(relx=1.0, rely=0.5, anchor="e", x=-16)

        self._select_preset("mp3")

    def _make_card(self, parent, key, info, row, col):
        card = ctk.CTkFrame(
            parent, fg_color=CARD_NORMAL,
            corner_radius=10, border_width=2,
            border_color="#3a3a3a", cursor="hand2"
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(pady=10, padx=12)

        ctk.CTkLabel(inner, text=info["icon"],
                     font=ctk.CTkFont(size=18)).pack()
        ctk.CTkLabel(inner, text=info["label"],
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="white").pack()
        ctk.CTkLabel(inner, text=info["sub"],
                     font=ctk.CTkFont(size=10),
                     text_color="#888888").pack()

        for widget in [card, inner] + list(inner.winfo_children()):
            widget.bind("<Button-1>", lambda e, k=key: self._select_preset(k))

        self.preset_buttons[key] = card

    def _select_preset(self, key):
        self.selected_preset = key
        for k, card in self.preset_buttons.items():
            if k == key:
                card.configure(border_color=ACCENT, fg_color="#2a1215")
            else:
                card.configure(border_color="#3a3a3a", fg_color=CARD_NORMAL)

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.settings["download_dir"])
        if d:
            self.settings["download_dir"] = d
            save(self.settings)
            self.dir_label.configure(state="normal")
            self.dir_label.delete(0, "end")
            self.dir_label.insert(0, d)
            self.dir_label.configure(state="disabled")

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, color="#888888"):
        self.status_label.configure(text=text, text_color=color)

    def _run_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("FetchVid", "Please paste a video URL first.")
            return

        self.progress.set(0)
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self._set_status("Starting download...", "#aaaaaa")

        cmd = build_command(self.selected_preset, url, self.settings["download_dir"])
        self._log(f"▶ {to_string(cmd)}\n")

        def on_line(line):
            self.after(0, self._log, line)
            if "[download]" in line and "%" in line:
                try:
                    pct = float(line.split("%")[0].split()[-1]) / 100
                    self.after(0, self.progress.stop)
                    self.after(0, self.progress.configure, {"mode": "determinate"})
                    self.after(0, self.progress.set, pct)
                    self.after(0, self._set_status,
                               f"Downloading... {int(pct*100)}%", "#aaaaaa")
                except:
                    pass

        def on_done(rc):
            self.after(0, self.progress.stop)
            if rc == 0:
                self.after(0, self.progress.set, 1)
                self.after(0, self._set_status, "✅ Download complete!", "#4caf50")
            else:
                self.after(0, self.progress.set, 0)
                self.after(0, self._set_status, "❌ Download failed.", "#E63946")

        run(cmd, on_line=on_line, on_done=on_done)