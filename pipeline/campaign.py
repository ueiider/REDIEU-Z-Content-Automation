# -*- coding: utf-8 -*-
"""REDIEU Z campaign renderer. Usage: python pipeline/campaign.py images|reels|manifests [package-id ...]
Original procedural art only (Pillow). Reels: edge-tts narration (free) + animated frames piped to ffmpeg."""
import asyncio, json, math, pathlib, random, subprocess, sys, wave, datetime, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from campaign_data import PACKAGES, SRC, LABEL, TAGS

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "campaign"
VID = ROOT / "content" / "video"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FD = pathlib.Path("C:/Windows/Fonts")
IMPACT, BOLD, REG = str(FD / "impact.ttf"), str(FD / "segoeuib.ttf"), str(FD / "segoeui.ttf")
THEMES = {  # vertical gradient stops, sun colors
    "sunset": ([(24, 8, 58), (110, 24, 120), (240, 64, 130), (255, 150, 70)], ((255, 214, 90), (255, 70, 140))),
    "teal":   ([(4, 18, 44), (8, 64, 112), (0, 150, 168), (255, 120, 150)], ((255, 236, 150), (255, 100, 150))),
    "night":  ([(6, 6, 24), (30, 18, 84), (96, 36, 140), (230, 70, 150)], ((255, 200, 120), (200, 60, 200))),
}
ACCENT = (255, 70, 140)
VOICES = {"en": "en-US-AndrewNeural", "pt": "pt-BR-AntonioNeural"}
LI = {"en": 0, "pt": 1}
_font = {}
_bg = {}

def font(path, size):
    k = (path, size)
    if k not in _font:
        _font[k] = ImageFont.truetype(path, size)
    return _font[k]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def gradient(w, h, stops):
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        px[0, y] = lerp(stops[i], stops[i + 1], t - i)
    return img.resize((w, h))

def palm(d, x, y, height, lean, s):
    """Silhouette palm: curved trunk + 9 tapered fronds. Drawn at supersampled scale s."""
    col = (10, 6, 26)
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((x + lean * (t ** 2) * height, y - t * height))
    for i in range(20):
        w = int((16 - 8 * i / 20) * s)
        d.line([pts[i], pts[i + 1]], fill=col, width=w)
    tx, ty = pts[-1]
    for k in range(9):
        ang = math.radians(-170 + k * 20 + random.Random(k).uniform(-6, 6))
        ln = height * 0.42
        prev = (tx, ty)
        for j in range(1, 9):
            u = j / 8
            px_ = tx + math.cos(ang) * ln * u
            py_ = ty + math.sin(ang) * ln * u + (u ** 2) * ln * 0.55
            d.line([prev, (px_, py_)], fill=col, width=max(2, int((11 - 9 * u) * s)))
            prev = (px_, py_)

def background(theme, w, h):
    key = (theme, w, h)
    if key in _bg:
        return _bg[key].copy()
    s = 2
    W, H = w * s, h * s
    stops, (c1, c2) = THEMES[theme]
    img = gradient(W, H, stops)
    d = ImageDraw.Draw(img)
    r = int(min(W, H) * 0.27)
    cx, cy = W // 2, int(H * (0.37 if h > w else 0.40))
    sun = Image.new("RGB", (2 * r, 2 * r))
    sun.paste(gradient(2 * r, 2 * r, [c1, c2]))
    m = Image.new("L", (2 * r, 2 * r), 0)
    md = ImageDraw.Draw(m)
    md.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    for i in range(9):  # synthwave stripes cut from lower half
        y0 = int(r * (1.05 + i * 0.105))
        md.rectangle([0, y0, 2 * r, y0 + int(2 + i * 3.2) * s], fill=0)
    img.paste(sun, (cx - r, cy - r), m)
    hz = int(H * 0.72)  # skyline + grid floor
    rnd = random.Random(7)
    x = 0
    while x < W:
        bw = rnd.randint(60, 150) * s // 2
        bh = rnd.randint(60, 300) * s // 2
        d.rectangle([x, hz - bh, x + bw, hz], fill=(14, 8, 34))
        x += bw + rnd.randint(0, 14)
    d.rectangle([0, hz, W, H], fill=(12, 6, 30))
    for i in range(1, 14):
        yy = hz + int((i / 14) ** 2.2 * (H - hz))
        d.line([(0, yy), (W, yy)], fill=(150, 40, 150), width=2 * s)
    for i in range(-10, 11):
        d.line([(W // 2 + i * 14 * s, hz), (W // 2 + i * 150 * s, H)], fill=(150, 40, 150), width=s + 1)
    palm(d, int(W * 0.06), H, int(H * 0.50), 0.10, s)
    palm(d, int(W * 0.94), H, int(H * 0.42), -0.12, s)
    img = img.resize((w, h), Image.LANCZOS)
    _bg[key] = img
    return img.copy()

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    return lines + ([cur] if cur else [])

def fit(d, text, path, start, maxw, maxlines, minsize=40):
    size = start
    while size > minsize:
        f = font(path, size)
        ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines and all(d.textlength(l, font=f) <= maxw for l in ls):
            return f, ls
        size -= 4
    f = font(path, minsize)
    return f, wrap(d, text, f, maxw)

def shadow_text(d, xy, text, f, fill, anchor="la"):
    x, y = xy
    d.text((x + 3, y + 4), text, font=f, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor)

def chip(d, x, y, text, f, fill, fg=(12, 8, 30), anchor_right=False):
    tw = d.textlength(text, font=f)
    pad = 26
    x0 = x - tw - 2 * pad if anchor_right else x
    d.rounded_rectangle([x0, y, x0 + tw + 2 * pad, y + f.size + 24], 14, fill=fill)
    d.text((x0 + pad, y + 10), text, font=f, fill=fg)

def card(pkg, idx, lang, size, total=None, hint=True, reel=False):
    """Render slide idx of package in language lang to RGBA->RGB image. size=(W,H)."""
    W, H = size
    li = LI[lang]
    sl = pkg["slides"][idx]
    img = background(pkg["theme"], W, H).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    top = 250 if reel else 70
    bottom_pad = 420 if reel else 110
    mx = 80
    # content panel
    py0 = int(H * 0.30) if not reel else 340
    py1 = H - bottom_pad - (30 if not reel else 360)
    od.rounded_rectangle([mx - 20, py0, W - mx + 20, py1], 34, fill=(8, 4, 24, 170))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img)
    # brand + chip
    d.text((mx, top), "REDIEU", font=font(IMPACT, 54), fill="white")
    bx = mx + d.textlength("REDIEU", font=font(IMPACT, 54))
    d.text((bx, top), "·Z", font=font(IMPACT, 54), fill=ACCENT)
    chip(d, W - mx, top - 4, LABEL[pkg["cls"]][li], font(BOLD, 28), ACCENT if pkg["cls"] != "ANALYSIS" else (120, 200, 255), anchor_right=True)
    # content block, vertically centered in panel
    maxw = W - 2 * mx - 40
    blocks = []
    if sl["big"]:
        f, ls = fit(d, sl["big"][li], IMPACT, 250 if not reel else 300, maxw, 1, 90)
        blocks.append(("big", f, ls, f.size * 1.05))
    if sl["h"]:
        f, ls = fit(d, sl["h"][li], IMPACT, 104 if not sl["big"] else 78, maxw, 3, 52)
        blocks.append(("h", f, ls, f.size * 1.08))
    if sl["b"]:
        f, ls = fit(d, sl["b"][li], BOLD, 50, maxw, 6, 32)
        blocks.append(("b", f, ls, f.size * 1.32))
    if sl["items"]:
        its = sl["items"][li]
        f = font(BOLD, 46 if len(its) <= 4 else 40)
        rows = []
        for t in its:
            rows.append(wrap(d, t, f, maxw - 60))
        blocks.append(("items", f, rows, f.size * 1.3))
    def bh(b):
        k, f, ls, lh = b
        if k == "items":
            return sum(len(r) * lh + 18 for r in ls)
        return len(ls) * lh
    gap = 26
    total_h = sum(bh(b) for b in blocks) + gap * (len(blocks) - 1)
    y = py0 + ((py1 - py0) - total_h) / 2
    for k, f, ls, lh in blocks:
        if k == "big":
            g = Image.new("RGBA", (W, int(lh) + 40), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            for ln in ls:
                gd.text((W // 2, 10), ln, font=f, fill=(255, 190, 90, 255), anchor="ma")
            mask = g.split()[3]
            grad = gradient(W, g.size[1], [(255, 220, 100), (255, 80, 150)]).convert("RGBA")
            sh = Image.new("RGBA", g.size, (0, 0, 0, 0))
            sh.paste((0, 0, 0, 255), (4, 5), mask)
            img.alpha_composite(sh, (0, int(y)))
            grad.putalpha(mask)
            img.alpha_composite(grad, (0, int(y)))
            d = ImageDraw.Draw(img)
            y += lh
        elif k == "h":
            for ln in ls:
                shadow_text(d, (W // 2, y), ln, f, "white", "ma")
                y += lh
        elif k == "b":
            for ln in ls:
                shadow_text(d, (W // 2, y), ln, f, (235, 232, 250), "ma")
                y += lh
        else:
            for row in ls:
                d.rectangle([mx + 6, y + f.size * 0.38, mx + 26, y + f.size * 0.38 + 20], fill=ACCENT)
                for ln in row:
                    d.text((mx + 56, y), ln, font=f, fill="white")
                    y += lh
                y += 18
        y += gap
    # footer
    fy = H - (130 if reel else 96)
    foot = {"en": "Fan page · Not affiliated with Rockstar Games · Source: Rockstar Newswire",
            "pt": "Página de fã · Sem afiliação com a Rockstar Games · Fonte: Rockstar Newswire"}[lang]
    if reel:
        fy = H - 470
    f26 = font(REG, 25)
    d.text((W // 2, fy), foot, font=f26, fill=(215, 210, 235), anchor="ma")
    if total and total > 1 and not reel:
        d.text((W - mx, fy - 60), f"{idx + 1}/{total}", font=font(BOLD, 34), fill="white", anchor="ra")
        if idx == 0 and hint:
            d.text((mx, fy - 60), "SWIPE  ›" if lang == "en" else "ARRASTE  ›", font=font(BOLD, 34), fill=ACCENT)
    return img.convert("RGB")

def paths(pkg, lang, n=None, kind=None):
    base = OUT / pkg["id"]
    base.mkdir(parents=True, exist_ok=True)
    return base

def render_images(pkgs):
    n = 0
    for pkg in pkgs:
        base = paths(pkg, "en")
        for lang in ("en", "pt"):
            if pkg["kind"] == "reel":
                cv = card(dict(pkg), 0, lang, (1080, 1920), reel=True)
                cv.save(base / f"cover.{lang}.1080x1920.png", optimize=True); n += 1
                continue
            tot = len(pkg["slides"])
            for i in range(tot):
                card(pkg, i, lang, (1080, 1350), total=tot).save(base / f"{lang}.slide{i + 1}.1080x1350.png", optimize=True); n += 1
            if pkg["kind"] == "image":
                card(pkg, 0, lang, (1080, 1080)).save(base / f"{lang}.square.1080x1080.png", optimize=True); n += 1
            card(pkg, 0, lang, (1080, 1920), reel=True).save(base / f"cover.{lang}.1080x1920.png", optimize=True); n += 1
        print("images", pkg["id"])
    return n

# ---------------- Reels ----------------
def say_text(sl, lang):
    li = LI[lang]
    if sl["say"]:
        return sl["say"][li]
    parts = [sl[k][li] for k in ("big", "h", "b") if sl[k]]
    if sl["items"]:
        parts += sl["items"][li]
    return ". ".join(parts)

async def _tts(text, voice, path):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="+0%").save(str(path))

def to_wav(src, dst):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(src), "-ar", "44100", "-ac", "1", str(dst)], check=True)

def chunk(text, maxc=34):
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > maxc and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])

def reel_frame(pkg, lang, base_img, sub, t_in, t_scene, zoom):
    """Compose one animated frame: zoomed bg already inside base_img; add subtitle bar + progress."""
    W, H = 1080, 1920
    img = base_img
    if zoom > 1.0:
        w2, h2 = int(W * zoom), int(H * zoom)
        z = img.resize((w2, h2), Image.BILINEAR)
        img = z.crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    return img

def render_reel(pkg, lang):
    li = LI[lang]
    VID.mkdir(parents=True, exist_ok=True)
    out = VID / f"{pkg['id']}.{lang}.mp4"
    work = VID / "_work" / f"{pkg['id']}.{lang}"
    work.mkdir(parents=True, exist_ok=True)
    fps = 24
    scenes = []
    for i, sl in enumerate(pkg["slides"]):
        txt = say_text(sl, lang)
        mp3, wav = work / f"s{i}.mp3", work / f"s{i}.wav"
        if not wav.exists():
            asyncio.run(_tts(txt, VOICES[lang], mp3))
            to_wav(mp3, wav)
        with wave.open(str(wav)) as w:
            frames = w.readframes(w.getnframes()); sr = w.getframerate()
        dur = len(frames) / 2 / sr
        scenes.append((txt, frames, dur))
    gap = int(0.35 * 44100) * 2
    audio = b"".join(s[1] + b"\x00" * gap for s in scenes) + b"\x00" * int(0.6 * 44100) * 2
    awav = work / "audio.wav"
    with wave.open(str(awav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100); w.writeframes(audio)
    total = len(audio) / 2 / 44100
    cmd = [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(fps), "-i", "-",
           "-i", str(awav), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k",
           "-t", f"{total:.2f}", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fsub = font(BOLD, 52)
    nfr = 0
    for i, (txt, _, dur) in enumerate(scenes):
        base = card(pkg, i, lang, (1080, 1920), reel=True).convert("RGB")
        chunks = chunk(txt)
        weights = [len(c) for c in chunks]
        tot_w = sum(weights) or 1
        starts, acc = [], 0.0
        for wgt in weights:
            starts.append(acc); acc += dur * wgt / tot_w
        scene_len = dur + 0.35
        n = int(round(scene_len * fps))
        for fr in range(n):
            t = fr / fps
            e = min(1.0, t / 0.35)  # ease-in fade for the scene
            zf = 1.0 + 0.05 * (t / max(scene_len, 0.1))
            im = reel_frame(pkg, lang, base, None, t, scene_len, zf).copy()
            d = ImageDraw.Draw(im, "RGBA")
            # active subtitle chunk
            ci = max(k for k in range(len(chunks)) if starts[k] <= t) if chunks else 0
            if chunks and t <= dur + 0.2:
                lines = wrap(d, chunks[ci], fsub, 900)
                bh = len(lines) * 66 + 36
                y0 = 1180
                d.rounded_rectangle([60, y0, 1020, y0 + bh], 26, fill=(0, 0, 0, 175))
                for li_, ln in enumerate(lines):
                    d.text((540, y0 + 18 + li_ * 66), ln, font=fsub, fill="white", anchor="ma")
            if e < 1.0:
                fade = Image.new("RGB", im.size, (8, 4, 24))
                im = Image.blend(fade, im, 0.35 + 0.65 * e)
            gt = sum(s[2] + 0.35 for s in scenes[:i]) + t
            d2 = ImageDraw.Draw(im)
            d2.rectangle([0, 1900, int(1080 * gt / total), 1912], fill=ACCENT)
            p.stdin.write(im.tobytes()); nfr += 1
    p.stdin.close(); p.wait()
    print("reel", out.name, f"{total:.1f}s", nfr, "frames")
    return out

def render_reels(pkgs):
    for pkg in pkgs:
        if pkg["kind"] != "reel":
            continue
        for lang in ("en", "pt"):
            render_reel(pkg, lang)

# ---------------- manifests ----------------
def build_manifests(pkgs):
    mdir = ROOT / "content" / "manifests"
    mdir.mkdir(parents=True, exist_ok=True)
    for old in mdir.glob("gta6-*.json"):
        old.unlink()  # superseded by the 20-package campaign
    for pkg in pkgs:
        lang = pkg["lang"]
        en, pt = pkg["caption"]
        src_lines = "\n".join(f"- {SRC[k]}" for k in pkg["sources"])
        disc = ("Source: Rockstar Games Newswire / press (links in the first comment is not used; see below).")
        caption = (f"{en}\n\n—\n\n{pt}\n\n"
                   f"Fan page. Not affiliated with Rockstar Games or Take-Two. Página de fã, sem afiliação com a Rockstar Games ou a Take-Two.\n"
                   f"Source / Fonte: rockstargames.com/newswire\n\n{TAGS[0]}")
        base = OUT / pkg["id"]
        if pkg["kind"] == "image":
            assets = [f"content/campaign/{pkg['id']}/{lang}.slide1.1080x1350.png"]
        elif pkg["kind"] == "carousel":
            assets = [f"content/campaign/{pkg['id']}/{lang}.slide{i + 1}.1080x1350.png" for i in range(len(pkg["slides"]))]
        else:
            assets = [f"content/video/{pkg['id']}.{lang}.mp4"]
        when = pkg["when"]
        brt = (datetime.datetime.fromisoformat(when.replace("Z", "")) - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M BRT")
        for plat in ("instagram", "facebook"):
            m = dict(package_id=pkg["id"], platform=plat, kind=pkg["kind"], language=lang, class_=pkg["cls"],
                     scheduled_utc=when, scheduled_local=brt, caption=caption, sources=[SRC[k] for k in pkg["sources"]],
                     assets=assets, cover=f"content/campaign/{pkg['id']}/cover.{lang}.1080x1920.png",
                     status="READY_TO_PUBLISH", post_url=None, platform_post_id=None, error=None)
            m["class"] = m.pop("class_")
            (mdir / f"{pkg['id']}.{plat}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("manifests", len(pkgs) * 2)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "images"
    ids = sys.argv[2:]
    pk = [p for p in PACKAGES if not ids or p["id"] in ids or any(p["id"].startswith(i) for i in ids)]
    if cmd == "images":
        print("total images", render_images(pk))
    elif cmd == "reels":
        render_reels(pk)
    elif cmd == "manifests":
        build_manifests(pk)

