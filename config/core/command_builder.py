import os

PRESETS = {
    "mp3":       ["-x", "--audio-format", "mp3", "--audio-quality", "0"],
    "m4a":       ["-x", "--audio-format", "m4a", "--audio-quality", "0"],
    "best":      ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv"],
    "mp4_1080":  ["-f", "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=1080]", "--merge-output-format", "mp4"],
    "mp4_720":   ["-f", "bestvideo[height<=720][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=720]", "--merge-output-format", "mp4"],
    "mkv_4k":    ["-f", "bestvideo[height<=2160]+bestaudio/best", "--merge-output-format", "mkv"],
}

def build_command(preset, url, download_dir):
    flags = PRESETS.get(preset, PRESETS["mp3"])
    output = os.path.join(download_dir, "%(title)s.%(ext)s")
    return ["yt-dlp"] + flags + ["-o", output, url]

def to_string(cmd):
    return " ".join(f'"{p}"' if " " in p else p for p in cmd)