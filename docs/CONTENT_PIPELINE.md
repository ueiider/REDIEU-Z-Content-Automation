# Pipeline
1. Add stories to `content/queue/stories.json` (class, bilingual text, sources).
2. `python3 pipeline/render.py` creates images and manifests.
3. `python3 pipeline/validate.py` is the QC gate.
4. `python3 pipeline/publish_meta.py` is a dry run; add `--live` with env `META_PAGE_ID`, `META_PAGE_TOKEN`, `META_IG_USER_ID`, `IG_IMAGE_BASE_URL` (Instagram requires a public image URL).
Status is written back to each manifest. Only the platform's returned ID may set PUBLISHED.
