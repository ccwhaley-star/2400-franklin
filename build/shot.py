# Headless-Chrome screenshot. usage: python -I shot.py <html path> <out.png> <width> [height]
# height defaults to 3× width (enough for a phone "first screens" view); pass 9000 for a full page.
import sys, subprocess, os
html, out, w = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), int(sys.argv[3])
h = int(sys.argv[4]) if len(sys.argv) > 4 else w*3
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
url = "file:///" + html.replace("\\", "/")
cmd=[chrome,"--headless=new","--disable-gpu","--hide-scrollbars","--no-sandbox",
     f"--window-size={w},{h}",f"--screenshot={out}","--virtual-time-budget=5000",url]
subprocess.run(cmd, capture_output=True, timeout=120)
print(out, os.path.getsize(out) if os.path.exists(out) else "FAILED")
