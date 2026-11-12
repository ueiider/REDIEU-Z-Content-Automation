# Implementation Roadmap — Fully Automated Multi-Platform Publishing

Written 2026-11-12 from the evidence in `11_Audit/`. Extends (does not replace) `ROADMAP.md`.
**Standing rules for every phase:** human approval before any public post; first tests are `private`/`unlisted`/`SELF_ONLY`; no secret values in git, logs or chat; never touch port 8000 (Revit MCP); do not publish footage whose rights are not cleared; stages stay separate (a failed publish never deletes a render).

Phases are ordered by dependency. Items marked 👤 need a human action (account, console, consent screen).

---

## Phase 0 — Stabilise and make state trustworthy (about 1 day)
- [ ] Put `Pipeline\` under git (private); exclude media/work/logs.
- [ ] Fix queue hygiene: atomic writes in `ctl.py stop`; re-queue (not fail) interrupted items; single-instance lock for the worker (audit C1–C3).
- [ ] Make `discover_gta6.py` use the real current date and a configurable yt-dlp path (C4).
- [ ] Merge this documentation branch after review; keep `PROGRESS_TRACKER_VERIFIED_*` updated.
- **Exit:** `ctl.py status` is accurate after a deliberate stop/start; Pipeline has a commit history.

## Phase 1 — Make the videos publishable (rights + relevance) — largest effort
- [ ] 👤 Decide the footage policy: own PS5 captures, licensed/stock packs, or explicit permission. Until then videos stay "editing tests".
- [ ] Add per-scene `visual` mapping to `scripts.json` (`asset`, `start`, `end`, `credit`, `rights`) and make the renderer consume it; refuse scenes without a rights-cleared asset (B1, A7).
- [ ] Build a small licensed asset library under `02_Raw_Clips\` with a `library.json` index (tags, licence, source).
- [ ] Watermark to spec: `@REDIEUZ`, away from top edge (B2, B5). Choose licensed music and mix with ducking (B3).
- [ ] Forced alignment with `faster-whisper` for caption timing (B4).
- [ ] Optional bake-off vs MoneyPrinterTurbo/PurffleShorts on the same script (docs requirement); keep the best parts.
- **Exit:** three consecutive videos pass the human visual-relevance review with all assets flagged rights-cleared.

## Phase 2 — Automated QC and approval gate
- [ ] QC step after render: ffprobe resolution/fps/duration, loudness within ±1 LU of target, black-frame and silence detection, caption overflow check, sidecar completeness (title, description, hashtags, **source citation per confirmed claim**, rights flag).
- [ ] Fact-check evidence: every `confirmed` scene stores a URL/citation to Rockstar material in the sidecar (D1). Rumor scenes store the source video id.
- [ ] Approval store `approval.json` per ID (`status: approved|rejected`, reviewer, timestamp, notes) written by a tiny local CLI/page. Queue states extended per `PUBLISHING_WORKFLOW.md` (`READY_FOR_REVIEW → APPROVED → QUEUED_FOR_PUBLISHING → PUBLISHING → PUBLISHED|FAILED`).
- **Exit:** an unapproved or QC-failed video cannot reach any publish call (tested).

## Phase 3 — YouTube end-to-end (first platform)
- [ ] 👤 Resolve token strategy: Testing-mode tokens expire in about 7 days [E]; either move the OAuth app to production (and plan for the unverified-project private-upload lock [E]) or schedule re-authorisation. Consider also granting `youtube.readonly` so channel identity can be verified (A4–A5).
- [ ] Start the Open-Dispatch **scheduler worker** and confirm `/healthz` shows it alive (A3); document how it is auto-started.
- [ ] Write the **publish bridge** (opportunity G1): approved MP4 → copy into `Open-Dispatch\media\incoming\` → `POST /dispatch` with `profile_id`, `privacy: private`, title/description/tags from sidecar → poll row → write `publications.json` (platform, row id, video id, URL, time, status). Idempotency key = Short ID, so a retry cannot double-upload (A1, A2, A8).
- [ ] Controlled test: one **private** upload of an approved test video; verify video ID, title, description, category, privacy, synthetic-content disclosure; delete the test video manually.
- [ ] Scheduled publishing test (`publishAt`) on a private video.
- **Exit:** a private test upload ID is recorded and verified by a human; a repeat run does not duplicate.

## Phase 4 — Instagram Reels
- [ ] 👤 Confirm an Instagram professional account; create a Meta developer app; obtain `instagram_content_publish`; long-lived token; app review as needed.
- [ ] Choose route: (a) PurffleShorts' direct resumable upload code (no public URL) — preferred for local-first; or (b) Open-Dispatch adapter + a temporary public URL host.
- [ ] Controlled test post (to a test/private account or immediately deleted) and record the media id.
- **Exit:** one Reel published to a controlled account via the bridge, id recorded.

## Phase 5 — Facebook Page Reels
- [ ] 👤 Page ID + Page access token with required permissions; app review.
- [ ] Decide whether `/videos` (what the Open-Dispatch adapter uses) is acceptable or Reels-edge support must be added; check the current Graph version (adapter pins v19.0).
- [ ] Controlled test.
- **Exit:** one Page video/Reel posted and recorded.

## Phase 6 — TikTok
- [ ] 👤 TikTok developer app; Content Posting API approval; domain/URL-prefix verification if using `PULL_FROM_URL`; understand audit status (unaudited ⇒ private-only posts [E]).
- [ ] Decide: own API (needs audit + public URL, or implement `FILE_UPLOAD`) vs Upload-Post relay (paid, third-party-held tokens). Record the decision in `DECISIONS_AND_DISCOVERIES.md`.
- [ ] Controlled `SELF_ONLY` test post.
- **Exit:** one private TikTok post recorded.

## Phase 7 — Unified orchestrator
- [ ] One queue (`content_queue.json` or SQLite) replacing the separate script/queue/publication files; states from `PUBLISHING_WORKFLOW.md`; per-platform sub-status; retry only when safe; publication log.
- [ ] Single scheduler (Windows Task Scheduler or one supervisor script) that runs: render worker, QC, publish bridge, Open-Dispatch worker; with health checks and notifications (webhook/Discord).
- [ ] Per-platform caption/title/hashtag adaptation (local LLM or templates), respecting each platform's length limits.
- **Exit:** a Short flows script → render → QC → (human approve) → three platforms with no manual file copying; failures visible in one place.

## Phase 8 — Research automation and feedback
- [ ] Scheduled discovery (fixed date handling), ranking by views/day, transcript analysis with a local model (choose/install one — Nemotron is currently absent), candidate topics → drafts → scripts with evidence.
- [ ] Analytics pull (YouTube `youtube.readonly` or API key; others as available) feeding topic ranking.
- **Exit:** weekly auto-generated topic list with sources; at least one approved Short per week traced end-to-end.

---

## Decisions needed from the owner (blocking)
1. Footage policy (what visuals may legally appear).
2. Is a third-party relay (Upload-Post) acceptable?
3. OAuth app: move to production / go through the YouTube API audit, or accept private-only automation.
4. Which local LLM is the standard (Nemotron vs the installed gemma4/qwen3).
5. Is `@REDIEUZ` the final watermark text and position?

## Risks to watch
Platform policy/audit delays (YouTube, TikTok, Meta); token expiry; Graph API version sunsets (adapters pin v19.0/v21.0); copyright strikes from trailer-derived footage; spam/automation policies on cross-posting identical content; Windows process fragility (no service manager).
