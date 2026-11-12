# Publishing setup: the exact actions needed

Status verified 2026-11-13: no Meta token on this notebook, built-in browser logged out of Meta, no Chrome extension connected. Open-Dispatch and Postiz are **not installed** on this notebook (Open-Dispatch lives on the main PC at `D:\GTA6_Content\Tools\Open-Dispatch`). Chosen route: **official Meta Graph API** via `pipeline/publish_campaign.py` (no extra software, no third-party credentials).

## Option A: Graph API (recommended, fully automatic)
1. Instagram account must be Professional (Business/Creator) and linked to your Facebook Page.
2. developers.facebook.com: create an app (Business type). Permissions: `pages_show_list`, `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`. While you are the app admin, development mode is enough for your own accounts.
3. Generate a long-lived **Page access token**; note the Page ID and the Instagram user ID (`GET /{page-id}?fields=instagram_business_account`).
4. Merge branch `claude/eager-archimedes-xf3e7q` into `main` so images are public at `https://raw.githubusercontent.com/ueiider/REDIEU-Z-Content-Automation/main/content/`.
5. Upload the MP4s (they are git-ignored) to a GitHub Release, e.g. `gh release create campaign-media-v1 content/video/*.mp4`, and use its download URL as `IG_VIDEO_BASE_URL` (Instagram needs a direct, non-redirecting URL; if it rejects the release URL, host the MP4s on any static host).
6. In PowerShell (never paste tokens into chat or commit them):
```powershell
$env:META_PAGE_TOKEN="..."; $env:META_PAGE_ID="..."; $env:META_IG_USER_ID="..."
$env:IG_MEDIA_BASE_URL="https://raw.githubusercontent.com/ueiider/REDIEU-Z-Content-Automation/main/content"
python pipeline/validate_campaign.py
python pipeline/publish_campaign.py            # dry run
python pipeline/publish_campaign.py --live --platform facebook   # Facebook uses native scheduling
python pipeline/publish_campaign.py --live --due --platform instagram   # run on a timer; Instagram has no API scheduling
```
7. Re-check Rockstar Newswire before each date-sensitive post (see CONTENT_CALENDAR.md). Manifests marked `BLOCKED_AUTH` are retried automatically on the next live run.

## Option B: Meta Business Suite (manual, no API)
Sign in at business.facebook.com/latest, then open the Composer and upload the files listed in each manifest (`content/manifests/pXX-*.json`): paste `caption`, upload `assets`, schedule at `scheduled_local`. Or sign in inside the Claude browser pane yourself and ask Claude to continue; it can schedule from the manifests (you must complete the login).

