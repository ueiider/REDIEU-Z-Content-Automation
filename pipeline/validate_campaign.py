# -*- coding: utf-8 -*-
"""QC gate for campaign manifests: asset existence, image sizes, caption length, sources, video specs. Exit 1 on failure."""
import json, pathlib, re, subprocess, sys
from PIL import Image
import imageio_ffmpeg
R = pathlib.Path(__file__).resolve().parent.parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
bad = 0
for p in sorted((R / "content/manifests").glob("p*.json")):
    m = json.load(open(p, encoding="utf-8")); errs = []
    if len(m["caption"]) > 2200: errs.append("caption >2200")
    if not m["sources"]: errs.append("no sources")
    if "not affiliated" not in m["caption"].lower(): errs.append("missing disclaimer")
    for a in m["assets"]:
        f = R / a
        if not f.exists(): errs.append("missing " + a); continue
        if a.endswith(".png"):
            if Image.open(f).size != (1080, 1350): errs.append("bad size " + a)
        else:
            o = subprocess.run([FF, "-hide_banner", "-i", str(f)], capture_output=True, text=True).stderr
            d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
            secs = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0
            if "1080x1920" not in o or "Video: h264" not in o or "Audio: aac" not in o: errs.append("bad video spec")
            if not 5 <= secs <= 90: errs.append(f"duration {secs}")
    print(("FAIL " if errs else "ok   ") + p.name, errs or ""); bad += bool(errs)
sys.exit(1 if bad else 0)
