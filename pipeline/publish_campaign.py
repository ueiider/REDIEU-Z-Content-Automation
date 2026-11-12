# -*- coding: utf-8 -*-
"""Publish campaign manifests through the official Meta Graph API. Dry-run by default.
Env (never commit): META_PAGE_ID, META_PAGE_TOKEN, META_IG_USER_ID, IG_MEDIA_BASE_URL (public base for content/ files),
IG_VIDEO_BASE_URL (public base for MP4 files, e.g. GitHub Release download URL).
Usage: publish_campaign.py [--live] [--due] [--platform instagram|facebook] [--id p01]
 --due   only items whose scheduled_utc has passed (Instagram has no API scheduling, so run this on a timer)
Facebook items are sent with native scheduling (scheduled_publish_time) when the slot is 10 min to 30 days ahead.
Auth/permission errors (400/401/403) are never retried."""
import datetime, json, os, pathlib, sys, time, requests

R = pathlib.Path(__file__).resolve().parent.parent
G = "https://graph.facebook.com/v21.0"
A = sys.argv
live, due = "--live" in A, "--due" in A
arg = lambda k: A[A.index(k) + 1] if k in A else None
only_plat, only_id = arg("--platform"), arg("--id")
tok, page, ig = (os.environ.get(k) for k in ("META_PAGE_TOKEN", "META_PAGE_ID", "META_IG_USER_ID"))
mbase, vbase = os.environ.get("IG_MEDIA_BASE_URL", ""), os.environ.get("IG_VIDEO_BASE_URL", "")
now = datetime.datetime.now(datetime.timezone.utc)

def call(method, path, **data):
    for i in range(3):
        r = requests.request(method, f"{G}/{path}", **({"params": {**data, "access_token": tok}} if method == "GET" else {"data": {**data, "access_token": tok}}), timeout=120)
        if r.ok:
            return r.json()
        if r.status_code in (400, 401, 403):
            raise RuntimeError(r.text[:400])
        time.sleep(2 ** i)
    raise RuntimeError(r.text[:400])

def url_for(asset):
    return (vbase.rstrip("/") + "/" + pathlib.Path(asset).name) if asset.endswith(".mp4") else mbase.rstrip("/") + "/" + asset.replace("content/", "", 1)

def wait_ready(cid):
    for _ in range(40):
        s = call("GET", cid, fields="status_code")
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") == "ERROR":
            raise RuntimeError("IG container ERROR")
        time.sleep(6)
    raise RuntimeError("IG container timeout")

def post_facebook(m, sched):
    extra = {"published": "false", "scheduled_publish_time": int(sched.timestamp())} if sched else {}
    if m["kind"] == "reel":
        with open(R / m["assets"][0], "rb") as f:
            r = requests.post(f"{G}/{page}/videos", data={"description": m["caption"], "access_token": tok, **extra}, files={"source": f}, timeout=900)
        r.raise_for_status(); return r.json()["id"]
    ids = []
    for a in m["assets"]:
        with open(R / a, "rb") as f:
            r = requests.post(f"{G}/{page}/photos", data={"published": "false", "access_token": tok}, files={"source": f}, timeout=120)
        r.raise_for_status(); ids.append(r.json()["id"])
    d = {"message": m["caption"], **extra}
    for i, pid in enumerate(ids):
        d[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
    return call("POST", f"{page}/feed", **d)["id"]

def post_instagram(m):
    if m["kind"] == "image":
        c = call("POST", f"{ig}/media", image_url=url_for(m["assets"][0]), caption=m["caption"])["id"]
    elif m["kind"] == "carousel":
        kids = [call("POST", f"{ig}/media", image_url=url_for(a), is_carousel_item="true")["id"] for a in m["assets"]]
        c = call("POST", f"{ig}/media", media_type="CAROUSEL", children=",".join(kids), caption=m["caption"])["id"]
    else:
        c = call("POST", f"{ig}/media", media_type="REELS", video_url=url_for(m["assets"][0]), caption=m["caption"], share_to_feed="true")["id"]
    wait_ready(c)
    mid = call("POST", f"{ig}/media_publish", creation_id=c)["id"]
    return mid, call("GET", mid, fields="permalink").get("permalink")

for p in sorted((R / "content/manifests").glob("p*.json")):
    m = json.load(open(p, encoding="utf-8"))
    if m["status"] not in ("READY_TO_PUBLISH", "SCHEDULED", "BLOCKED_AUTH") or (only_plat and m["platform"] != only_plat) or (only_id and not m["package_id"].startswith(only_id)):
        continue
    when = datetime.datetime.fromisoformat(m["scheduled_utc"].replace("Z", "+00:00"))
    if due and when > now:
        continue
    if not live:
        print("DRY-RUN", p.name, m["scheduled_local"]); continue
    try:
        if m["platform"] == "facebook":
            if not (tok and page): raise PermissionError("META_PAGE_TOKEN/META_PAGE_ID not set")
            lead = (when - now).total_seconds()
            sched = when if 600 < lead < 30 * 86400 else None
            if m["status"] == "SCHEDULED" and sched: continue
            m["platform_post_id"] = post_facebook(m, sched)
            m["status"] = "SCHEDULED" if sched else "PUBLISHED"
        else:
            if not (tok and ig and mbase): raise PermissionError("META_PAGE_TOKEN/META_IG_USER_ID/IG_MEDIA_BASE_URL not set")
            m["platform_post_id"], m["post_url"] = post_instagram(m); m["status"] = "PUBLISHED"
        m["error"] = None
    except PermissionError as e:
        m.update(status="BLOCKED_AUTH", error=str(e))
    except Exception as e:
        m.update(status="FAILED", error=str(e)[:400])
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(m["status"], p.name, m.get("error") or m.get("platform_post_id"))

