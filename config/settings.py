import json, os

SETTINGS_FILE = os.path.expanduser("~/.fetchvid.json")
DEFAULTS = {
    "download_dir": os.path.expanduser("~/Downloads"),
    "default_preset": "mp3",
}

def load():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return {**DEFAULTS, **json.load(f)}
    return DEFAULTS.copy()

def save(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)