"""Publish queued manifests via the official Meta Graph API. Default is dry-run.
Env (never commit): META_PAGE_ID, META_PAGE_TOKEN, META_IG_USER_ID. Usage: publish_meta.py [--live] [--lang en|pt]
Instagram needs a PUBLIC image URL (IG_IMAGE_BASE_URL + asset name), e.g. GitHub Pages docs/ folder."""
import json, os, pathlib, sys, time, datetime, requests
R = pathlib.Path(__file__).resolve().parent.parent; G = "https://graph.facebook.com/v21.0"
live = "--live" in sys.argv; lang = sys.argv[sys.argv.index("--lang")+1] if "--lang" in sys.argv else None
tok, page, ig, base = (os.environ.get(k) for k in ("META_PAGE_TOKEN", "META_PAGE_ID", "META_IG_USER_ID", "IG_IMAGE_BASE_URL"))
def call(path, **data):
    for i in range(3):
        r = requests.post(f"{G}/{path}", data={**data, "access_token": tok}, timeout=60)
        if r.ok: return r.json()
        if r.status_code in (400, 401, 403): raise RuntimeError(r.text)  # no blind retry on auth/permission errors
        time.sleep(2**i)
    raise RuntimeError(r.text)
for p in sorted((R/"content/manifests").glob("*.json")):
    m = json.load(open(p, encoding="utf-8"))
    if m["status"] != "READY_TO_PUBLISH" or (lang and m["language"] != lang): continue
    if not live: print("DRY-RUN", p.name); continue
    if not (tok and page): m.update(status="BLOCKED", error="META_PAGE_TOKEN/META_PAGE_ID not set")
    else:
        try:
            with open(R/m["asset"], "rb") as f:
                r = requests.post(f"{G}/{page}/photos", data={"caption": m["caption"], "access_token": tok}, files={"source": f}, timeout=120)
            r.raise_for_status(); m["facebook_post_id"] = r.json().get("post_id") or r.json().get("id")
            if ig and base:
                c = call(f"{ig}/media", image_url=base.rstrip("/")+"/"+pathlib.Path(m["asset"]).name, caption=m["caption"])
                m["instagram_media_id"] = call(f"{ig}/media_publish", creation_id=c["id"])["id"]
            m["status"] = "PUBLISHED"; m["published_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        except Exception as e: m.update(status="FAILED", error=str(e)[:500])
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2); print(m["status"], p.name, m.get("error") or "")
