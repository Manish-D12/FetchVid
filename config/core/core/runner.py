import subprocess, threading

def run(cmd, on_line, on_done):
    def _run():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                on_line(line.rstrip())
            proc.wait()
            on_done(proc.returncode)
        except FileNotFoundError:
            on_line("ERROR: yt-dlp not found. Run: pip install yt-dlp")
            on_done(1)
    threading.Thread(target=_run, daemon=True).start()