# Publishing Integrations Audit — YouTube, Instagram, TikTok, Facebook

Audit date: 2026-11-12. **No OAuth flow, API call, upload or credential change was performed by this audit.**
Legend: **[V]** verified in local source/config · **[E]** external platform rule from general knowledge of vendor documentation — *must be re-checked against current official docs before relying on it* · **[P]** pending/unverified.
Secrets rule: only locations, field names and set/empty state are recorded here. Values never.

---

## 1. YouTube — actual implementation

### 1.1 Google Cloud / OAuth app (from earlier project notes, not re-verified online) [P]
Project `redieu-z-automation`, YouTube Data API v3, OAuth client type **Desktop app** ("REDIEU Z Publisher"), audience External, **Testing** mode. (Console state was not accessible to this audit.)

### 1.2 Local artefacts under `D:\GTA6_Content\Secrets` [V]
| File | Role | Structure observed (keys only) |
|---|---|---|
| `youtube-oauth-client.json` | Google "installed app" client file | `installed: client_id, project_id, auth_uri, token_uri, auth_provider_x509_cert_url, client_secret, redirect_uris` |
| `youtube-token.json` | Authorised-user credentials (written by `google-auth` `creds.to_json()`) | `token, refresh_token, token_uri, client_id, client_secret, scopes, universe_domain, account, expiry` |
| `youtube_oauth_setup.py` | One-time interactive consent | `InstalledAppFlow.from_client_secrets_file(...).run_local_server(port=0, access_type="offline", prompt="consent")`; scopes list = **`youtube.upload` only** |
| `validate_youtube.py` | Token sanity check | Exchanges the refresh token at `oauth2.googleapis.com/token`, then calls `youtube/v3/channels?part=snippet&mine=true` and prints channel title/ID |

**Scope actually granted [V]:** `https://www.googleapis.com/auth/youtube.upload` — nothing else.

### 1.3 Consequences of the upload-only scope
- `channels.list?mine=true` normally requires a read-capable scope (`youtube.readonly` or `youtube`). `validate_youtube.py` was **not run** by this audit; with an upload-only token it is **expected to be rejected (HTTP 403 insufficient scope) [E]**. The earlier "PASS" status in the notes is therefore **unproven [P]**. Channel identity cannot be confirmed with this token via that call; options in the roadmap.
- Upload-only scope is the *least-privilege* choice and is sufficient for `videos.insert`.

### 1.4 How Open-Dispatch uses it [V]
- Adapter `adapters/youtube.py`: refresh-token exchange at `https://oauth2.googleapis.com/token`, then **resumable upload** (`POST https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status`, then `PUT` of the file to the returned session URL). It pins the session URL host to `*.googleapis.com` over HTTPS and streams the file.
- Credentials: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` (optional `_<ACCOUNT>` suffix).
- **Where the values live now [V, set/empty only]:** `.env` values are empty; the Open-Dispatch profile `REDIEU Z` (`~\.open-dispatch\profiles.json`) has all three YouTube fields non-empty. So the credentials reach the adapter **only if the queued unit carries that profile's id** (Compose UI profile selector or `profile_id` in the API payload).
- Input constraint: `youtube_short.video_path` must resolve **inside** `OPEN_DISPATCH_MEDIA_DIR` (absolute paths rejected). Metadata: `privacy` ∈ `public|unlisted|private`, **default `public`** if omitted — always send `private` or `unlisted` for tests.
- Status: the upload path has **never been exercised** (queue is empty; no worker running; no video ID has been recorded anywhere) **[V]**.

### 1.5 Alternative implementation in PurffleShorts [V]
`purffle_shorts/youtube.py`: `InstalledAppFlow` + local token file, scopes `youtube.upload` (+ optional `youtube`, `youtube.readonly`, `youtube.force-ssl`), resumable upload with backoff (max 8 retries), quota guard (`YT_DAILY_LIMIT`, default 6/day), `publishAt` scheduling (privacy forced to `private` until publish time), playlist add, caption upload (400 quota units), AI-content flag (`containsSyntheticMedia`). Settings `GOOGLE_CLIENT_SECRETS_FILE` and `YT_TOKEN_FILE` could point at the files in `Secrets` — format compatibility is **likely but untested [P]**.

### 1.6 Platform rules that affect go-live [E — verify]
1. **Testing-mode refresh tokens expire after about 7 days** for External apps with sensitive scopes such as `youtube.upload`. The token obtained on 2026-11-12 would stop working around 2026-11-19 unless the app is moved to production or re-authorised. Plan for re-auth or publishing status change.
2. **Unverified API projects (created after 2020-07-28) have uploaded videos locked to private** until the project passes a YouTube API Services compliance audit. Public automated publishing may therefore be impossible before audit even with valid OAuth.
3. **Quota:** the default allocation is 10,000 units/day and `videos.insert` costs about 1,600 units → roughly 6 uploads per day (consistent with PurffleShorts' default).
4. Synthetic/AI-generated content disclosure: YouTube asks creators to disclose realistic altered or synthetic media; narration is TTS and footage is trailer-derived — decide the correct disclosure during review.

---

## 2. Instagram (Reels) — planned; **nothing configured**

| Path | Status |
|---|---|
| Open-Dispatch `adapters/instagram.py` [V] | Graph API `v21.0`. Reel requires `video_url` = **public HTTPS URL**; local paths are not supported (file header states this). Env: `IG_USER_ID`, `IG_TOKEN` (profile fields `user_id`, `token`). Polls container status (90 s default). |
| PurffleShorts `crosspost.instagram_direct` [V] | Graph API with **resumable upload straight from disk** (`rupload.facebook.com`); no public URL needed; publishes immediately (no scheduling). Env: `INSTAGRAM_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_API_VERSION`. |
| Credentials present anywhere? | **No** — `IG_*` empty in Open-Dispatch `.env`, no Instagram block in the profile; PurffleShorts `.env` not read **[P]** |
Requirements [E]: Instagram professional (creator/business) account; Meta developer app; `instagram_content_publish` permission; for accounts other than app testers, app review / business verification; long-lived token management. Reels video specs (9:16, duration/size limits) to be checked against current Meta docs.

## 3. Facebook (Page Reels/videos) — planned; **nothing configured**

| Path | Status |
|---|---|
| Open-Dispatch `adapters/facebook.py` [V] | Graph API `v19.0`; video posts use `POST /{page_id}/videos` with **`file_url`** (public URL). Uses the generic videos edge, **not** the Reels publishing edge. Env: `FACEBOOK_PAGE_ID`, `FACEBOOK_ACCESS_TOKEN`. |
| PurffleShorts [V] | No direct Facebook route; only through Upload-Post relay. |
| Credentials present? | **No.** |
Requirements [E]: Facebook Page, Page access token with page publishing permissions, app review for production use. `v19.0` is an old pinned Graph version and may be sunset — check before use.

## 4. TikTok — planned; **nothing configured**

| Path | Status |
|---|---|
| Open-Dispatch `adapters/tiktok.py` [V] | Content Posting API `https://open.tiktokapis.com/v2`, `source = PULL_FROM_URL` (TikTok fetches the video from a URL), token scope `video.publish`, env `TIKTOK_ACCESS_TOKEN`, `TIKTOK_PRIVACY_LEVEL`. |
| PurffleShorts [V] | States TikTok **always** goes via Upload-Post because TikTok's own API only lets audited apps publish public videos; Upload-Post's free plan excludes TikTok (paid plan needed). |
| Credentials present? | **No.** |
Requirements [E]: TikTok developer app; Content Posting API product approval; unaudited clients are typically restricted to private/`SELF_ONLY` posts until the app passes audit; `PULL_FROM_URL` requires the source domain/URL prefix to be verified with TikTok. Direct upload (`FILE_UPLOAD`) is not implemented in the Open-Dispatch adapter.

## 5. Cross-platform relay option — Upload-Post (third party)
Referenced by **both** PurffleShorts (`crosspost.py`) and MoneyPrinterTurbo (`app/services/upload_post.py`, currently disabled). Single API for TikTok, Instagram, Facebook, Threads, X, LinkedIn, Bluesky, Pinterest; holds the platform sign-ins on its servers. Trade-offs: external subscription (conflicts with the "no paid APIs / subscriptions" principle unless a free tier suffices), tokens stored by a third party (conflicts with "credentials never leave the machine"), but removes the need for app audits. Decision pending **[P]**.

## 6. Summary matrix

| Platform | Code path available locally | Credentials configured | Local file upload possible | Public-post blockers | Ever tested |
|---|---|---|---|---|---|
| YouTube | Open-Dispatch + PurffleShorts | Yes (profile; scope upload only) | Yes (media-root relative path) | token expiry in Testing mode; unverified-project private lock [E] | **No** |
| Instagram | Open-Dispatch (URL) / PurffleShorts (direct) | No | PurffleShorts only | Meta app review; token | No |
| Facebook | Open-Dispatch (URL) / Upload-Post | No | No (URL) | Page token, app review | No |
| TikTok | Open-Dispatch (URL pull) / Upload-Post | No | No | API audit, domain verification, paid relay | No |
