"""Render bilingual 1080x1350 news cards from content/queue/stories.json (Pillow only, original procedural art)."""
import json, hashlib, pathlib, textwrap, datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1350
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TAG = {"CONFIRMED": (255, 90, 120), "ANALYSIS": (120, 200, 255), "RUMOR": (255, 200, 80)}
def bg(seed):
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        t = y / H
        c = (int(255*(0.95-0.7*t)), int(80+60*t), int(150+80*t*0.6))
        for x in range(0, W): px[x, y] = tuple(int(v*(0.35+0.65*(1-abs(x-W/2)/W*0.6))) for v in c)
    d = ImageDraw.Draw(img)
    s = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
    for i in range(7):  # palm-less abstract skyline silhouette
        bw = 90 + (s >> i) % 80; bh = 180 + ((s >> (i+3)) % 260)
        x = i*160 - 20; d.rectangle([x, H-bh-120, x+bw, H], fill=(14, 10, 30))
    d.ellipse([W/2-190, 330, W/2+190, 710], fill=(255, 150, 90))
    return img.filter(ImageFilter.GaussianBlur(2))
def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines+[cur]
def card(story, lang):
    img = bg(story["id"]); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    o.rectangle([0, 760, W, H], fill=(8, 6, 20, 215)); img = Image.alpha_composite(img.convert("RGBA"), ov); d = ImageDraw.Draw(img)
    col = TAG[story["class"]]; lab = story["label"][lang]
    f = ImageFont.truetype(F, 40); d.rounded_rectangle([60, 800, 60+d.textlength(lab, font=f)+50, 868], 14, fill=col); d.text((85, 812), lab, font=f, fill=(10, 10, 20))
    y = 900; fh = ImageFont.truetype(F, 78)
    for l in wrap(d, story["headline"][lang], fh, W-120): d.text((60, y), l, font=fh, fill="white"); y += 92
    fb = ImageFont.truetype(FR, 40); y += 14
    for l in wrap(d, story["body"][lang], fb, W-120): d.text((60, y), l, font=fb, fill=(220, 220, 235)); y += 54
    ft = ImageFont.truetype(FR, 28)
    d.text((60, H-70), "REDIEU Z | Unofficial fan graphic, not affiliated with Rockstar", font=ft, fill=(160, 160, 185))
    return img.convert("RGB")
if __name__ == "__main__":
    stories = json.load(open(ROOT/"content/queue/stories.json", encoding="utf-8")); out = ROOT/"content/images"; out.mkdir(exist_ok=True, parents=True)
    for s in stories:
        for lang in ("en", "pt"):
            p = out/f"{s['id']}.{lang}.png"; card(s, lang).save(p, optimize=True)
            m = {"story_id": s["id"], "language": lang, "class": s["class"], "content_type": "image", "platforms": ["instagram", "facebook"],
                 "caption": s["caption"][lang], "sources": s["sources"], "asset": str(p.relative_to(ROOT)), "status": "READY_TO_PUBLISH",
                 "rendered_at": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()+"Z", "public_url": None, "error": None}
            (ROOT/"content/manifests"/f"{s['id']}.{lang}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            print("rendered", p.name)
