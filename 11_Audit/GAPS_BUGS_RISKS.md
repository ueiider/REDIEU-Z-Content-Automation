# Gaps, Limitations, Bugs, Risks and Integration Opportunities

Audit date: 2026-11-12. Severity: **H** blocks automated publishing or violates a project rule · **M** quality/reliability · **L** hygiene.
Each item states evidence. **[V]** verified locally · **[E]** external rule to re-check · **[P]** unverified.

---

## A. Blockers for end-to-end automated publishing

| # | Sev | Finding | Evidence |
|---|---|---|---|
| A1 | H | **Rendering and publishing are not connected.** Nothing moves a finished MP4 from `03_Shorts\Ready_For_Review` into Open-Dispatch or records approval. A person/agent copied files to `Open-Dispatch\media\incoming\` by hand. | No code references `Open-Dispatch` in `Pipeline\*.py`; `media\incoming` has copies, untracked in git [V] |
| A2 | H | **Open-Dispatch path restriction.** With `OPEN_DISPATCH_MEDIA_DIR` set, only media-root-relative paths work; `D:\GTA6_Content\03_Shorts\Ready_For_Review\...` is rejected. | `media/paths.py` (`absolute media paths are not allowed`), `.env` value [V] |
| A3 | H | **Open-Dispatch scheduler worker is not running**, so queued posts would never be sent. Only the API process (PID 13476) runs. | `/healthz` → `worker.running=false` [V] |
| A4 | H | **YouTube channel identity unverified.** Token scope is `youtube.upload` only; `validate_youtube.py` uses `channels.list?mine=true` which needs a read scope — "PASS" in earlier notes is unproven. No upload has ever been attempted. | Token `scopes` field; script source [V]; behaviour [E] |
| A5 | H | **Testing-mode token lifetime** (≈7 days for sensitive scopes) and **unverified-project private-only uploads**. Token issued 2026-11-12 may stop working ≈2026-11-19. | Google policy [E] |
| A6 | H | **Instagram, Facebook, TikTok: no credentials and (for Open-Dispatch) a public-URL requirement.** Local-first hosting cannot satisfy `video_url`/`file_url`/`PULL_FROM_URL` without a public host. | adapters `instagram.py`, `facebook.py`, `tiktok.py`; env empty [V] |
| A7 | H | **Footage rights.** All visuals are cut from one local official-trailer file; docs and requirements say rights for redistribution are *not* cleared. Publishing these would breach the project rule. | `worker.py` `FOOTAGE`; sidecar `footage_note` [V] |
| A8 | H | **Open-Dispatch defaults to `public`** when `privacy` is not set, and its API token is off by default. A careless `POST /dispatch` would publish publicly. | `adapters/youtube.py` `_build_metadata`; README [V] |

## B. Video-quality gaps (stated requirements not yet met)

| # | Sev | Finding | Evidence |
|---|---|---|---|
| B1 | H | **No narration-to-visual relevance.** Segment start offsets are arithmetic on item/scene index; `scripts.json` has no scene→asset mapping. Scenes about "fuel" or "weapon wheel" show arbitrary trailer moments. Project docs call this unacceptable. | `worker.py` offset formula; scene schema [V] |
| B2 | M | **Watermark does not match brand spec.** Docs: `@REDIEUZ`, away from the top edge. Implementation: text `REDIEU Z`, top-right, 55 px from top, ~50 % opacity. | `Style: Mark` in `worker.py`; `PROJECT_DEFINITION.md` [V] |
| B3 | M | **No background music**, only synthesised boom/whoosh/ding. Docs require licensed music with mixing. | `worker.py` audio stage [V] |
| B4 | M | **Caption timing is estimated** (proportional to character count) rather than aligned. Edge-TTS 7.x no longer provides word boundaries by default; forced alignment (faster-whisper, already a dependency in MPT/Chopify/PurffleShorts) would fix it. | `build_ass` [V] |
| B5 | M | **Badge/hook placement vs Shorts UI**: status badge sits at y≈125 px from top and the mark at 55 px — both inside the area platforms' UI can overlay. | styles in `worker.py` [V]; platform UI behaviour [E] |
| B6 | M | **No automated QC beyond resolution/duration** (no audio-level check, caption-overlap check, black-frame check, rights check, metadata completeness check). Docs require all. | `render()` verify block [V] |
| B7 | M | **Single 166 s source video** limits variety; many Shorts reuse the same shots. | `FOOTAGE` constant [V] |
| B8 | L | Metadata JSON lacks per-platform captions/titles, source URLs and fact-check evidence per claim. | sidecar schema [V] |

## C. Reliability and engineering issues in the Pipeline

| # | Sev | Finding |
|---|---|---|
| C1 | M | **Pipeline is not under version control.** One accidental overwrite loses it. |
| C2 | M | **No single-instance lock.** `worker.pid` is overwritten by any new worker; `ctl.py start` guards only via the PID file. Two workers could process the same pending item. |
| C3 | M | **Queue consistency:** `ctl.py stop` rewrites `queue.json` non-atomically while a worker may be writing. Observed queue shows `GTA6_Short_009` as `failed` with "interrupted render: worker stopped before completion", i.e. the stop/restart path produced a failure instead of a clean re-queue; the reset-on-start logic only covers `rendering`. |
| C4 | M | **`discover_gta6.py` hard-codes** the yt-dlp executable path and `TODAY = 2026-11-12`, so views-per-day ranking becomes wrong on any other date. |
| C5 | L | `ctl.py` liveness check matches the substring `python` in `tasklist`; a recycled PID of another Python process would look alive. |
| C6 | L | The worker is a run-to-empty batch, not a service: new queue entries added after it exits are not processed until `ctl.py start` is run again. No scheduler/cron or auto-start. |
| C7 | L | Edge-TTS needs internet; failures are retried once (`MAX_ATTEMPTS=2`) with a 10 s pause. No offline fallback voice. |
| C8 | L | Items are rendered strictly in queue order; no priority, no dependency on approval state. |

## D. Content-accuracy risks

| # | Sev | Finding |
|---|---|---|
| D1 | H | The `confirmed` badges (setting Leonida/Vice City, protagonists Lucia and Jason, platforms PS5/Xbox Series X\|S, Rockstar acknowledging the 2022 leak) were written from general knowledge, not from a stored Rockstar source reference. Each needs a citation (Rockstar Newswire/official trailer) in the sidecar JSON before approval. **[P]** |
| D2 | M | The `rumor` scripts are based on one third-party video transcript (source video id in `06_Scripts_Voice\Source_Transcripts\`). Claims are labelled unconfirmed, but the source's own reliability is unassessed. |
| D3 | M | No release-date statements were made on purpose; any future script that mentions dates must be re-verified on the day of rendering. |
| D4 | M | Model gap: docs promise Nemotron analysis; `ollama list` shows no Nemotron model. Provenance of `*_ai_clips.json` is **[P]**. |

## E. Security and secrets

| # | Sev | Finding |
|---|---|---|
| E1 | M | **Plaintext secrets in several places**: `Secrets\*.json`, Open-Dispatch `profiles.json` (+ a backup copy `profiles.json.backup_20261112_203226` — a second plaintext copy of whatever it contained), `Tools\MoneyPrinterTurbo\config.toml`, `Tools\PurffleShorts\.env`, `Tools\Open-Dispatch\.env`. All are outside the docs repo and covered by its `.gitignore`, but should be excluded from any cloud sync/backup that is not private. |
| E2 | M | MoneyPrinterTurbo `config.toml` sets `listen_host = 0.0.0.0` — if its API/WebUI is started it listens on all interfaces. Prefer `127.0.0.1`. |
| E3 | M | Open-Dispatch API token is optional/off; safe only because it is bound to 127.0.0.1. Any local process can queue posts. |
| E4 | L | `Secrets\youtube_oauth_setup.py` / `validate_youtube.py` are plain scripts next to the secrets; keep them out of the repo (they are; `Secrets/` is ignored). |

## F. Documentation drift found in the repo (as of base commit `cdd317d`)

- `README.md` references `10_AI_HANDOVER/…`; actual folder is `10_AI_Handover` (breaks on case-sensitive systems/GitHub links).
- `01_Project/CURRENT_STATUS.md` and `09_Roadmap/PROGRESS_TRACKER.md` are stale: queue now 002–008 and 010 completed, 009 failed, 011–014 pending (see verified tracker).
- `04_Tools/PURFFLE_SHORTS.md` presents PurffleShorts as the existing pipeline; the real pipeline is `Pipeline\worker.py`.
- `05_Integrations/YOUTUBE_OAUTH.md` lists the profile-credential gap as open; the profile *does* now contain YouTube credentials (set/empty check), but is untested.
- `TOOL_INVENTORY.md` lists Nemotron as intended; it is not installed in Ollama.

---

## G. Integration opportunities (ranked by value/effort)

1. **Publish bridge (high value, low effort):** small script that, for a human-approved ID, copies/links the MP4 into `Open-Dispatch\media\incoming\`, builds the `/dispatch` payload (`profile_id`, `privacy: private`) from the sidecar JSON, records the returned row id/URL in a `publications.json`. Uses only existing Open-Dispatch features.
2. **Scene-to-asset mapping (high value, medium effort):** add `visual` fields per scene (`asset`, `start`, `end`, `credit`) to `scripts.json`; renderer uses them instead of arithmetic offsets; refuse to render scenes without a licensed asset.
3. **Forced alignment for captions:** use `faster-whisper` (already installed in MPT/PurffleShorts/Chopify venvs) for true word timestamps; replaces the proportional estimate.
4. **Reuse PurffleShorts publishing code** as the Instagram direct-upload path (no public URL needed) and as a reference for scheduling/quota guard.
5. **Reuse MPT BGM and subtitle styling** after a side-by-side comparison on the same script (docs already require this).
6. **Local LLM drafting + fact-check pass** via Ollama (`gemma4`, `qwen3`) with an evidence field per claim.
7. **Human-approval UI**: a tiny local page/CLI listing `NEEDS_HUMAN_REVIEW` items with approve/reject writing `approval.json`; the publish bridge refuses unapproved items.
8. **Chopify** only after the channel owns legitimate long-form recordings.
9. **Put `Pipeline\` under git** (private repo or inside this docs repo as a sub-folder without media).
