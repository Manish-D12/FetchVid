import subprocess, json

def fetch(url):
    result = subprocess.run(
        ["yt-dlp", "-J", "--no-playlist", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    info = json.loads(result.stdout)
    return [
        {
            "id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution", "audio only"),
            "vcodec": f.get("vcodec", "none"),
            "acodec": f.get("acodec", "none"),
        }
        for f in info.get("formats", [])
    ]