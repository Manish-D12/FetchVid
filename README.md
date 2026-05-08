# FetchVid 🎬

A simple, fast video downloader for YouTube and other sites. Built with Python + yt-dlp.

## Features

- Download videos in MP3, M4A, MP4 720p, MP4 1080p, MKV 4K, or best available quality
- Clean dark UI
- Auto-installs yt-dlp on first run — no setup needed
- Remembers your download folder

## Download

Head to the [Releases](../../releases) page and download `FetchVid.exe`.

No Python, no pip, no setup. Just run the exe.

> **First launch:** A small setup window will appear for ~10 seconds while it downloads yt-dlp automatically. This only happens once.

## Running from Source

```bash
git clone https://github.com/Manish-D12/FetchVid.git
cd FetchVid
pip install customtkinter yt-dlp
python main.py
```

## Building the EXE

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name FetchVid main.py
```

Output will be in the `dist/` folder.

## Supported Sites

Anything yt-dlp supports — YouTube, Twitter/X, Instagram, TikTok, and [hundreds more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

Made by [Manish-D12](https://github.com/Manish-D12)
