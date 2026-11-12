"""QC gate: dimensions, caption presence, sources, duplicate detection. Exit 1 on failure."""
import json, pathlib, sys
from PIL import Image
R = pathlib.Path(__file__).resolve().parent.parent; bad = 0; seen = set()
for p in sorted((R/"content/manifests").glob("*.json")):
    m = json.load(open(p, encoding="utf-8")); errs = []
    if Image.open(R/m["asset"]).size != (1080, 1350): errs.append("bad dimensions")
    if not m["caption"].strip() or not m["sources"]: errs.append("missing caption/sources")
    k = (m["story_id"], m["language"])
    if k in seen: errs.append("duplicate")
    seen.add(k); print(("FAIL " if errs else "ok   ")+p.name, errs); bad += bool(errs)
sys.exit(1 if bad else 0)
