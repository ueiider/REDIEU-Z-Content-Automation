# Technical Audit — Tools, Versions, Dependencies, Capabilities

Audit date: 2026-11-12 (local time of the audited machine, UTC+11).
Method: read-only inspection of source, configuration structure and running listeners. Nothing was started, stopped, rendered, uploaded or modified.
Legend: **[V]** verified from source/config/live check · **[D]** declared by README/metadata but not executed · **[P]** pending / could not be verified.

---

## 1. Inventory at a glance

| Component | Upstream repository (from `git remote`) | Local path | Version / commit | Licence |
|---|---|---|---|---|
| MoneyPrinterTurbo (MPT) | https://github.com/harry0703/MoneyPrinterTurbo | `Tools\MoneyPrinterTurbo` | `pyproject` 1.3.10; `git describe` = `v1.3.10-12-gdd09658`; HEAD `dd096584f1642f3d52b8b2aa7c39df84bb2066bf` (2026-11-12) | MIT [V] |
| PurffleShorts | https://github.com/Chamanrajragu/purffle-shorts | `Tools\PurffleShorts` | `pyproject` 3.0.0; `v3.0.0-13-g38d49cd`; HEAD `38d49cd956319a73cf983153816acdbda3dc0e0c` (2026-11-03) | MIT [V] |
| Chopify | https://github.com/mehbul/chopify | `Tools\Chopify` | `v1.4.0-5-gd576927`; HEAD `d576927bf3b764733c97ac1ad324aa9957b0885d` (2026-11-06) | MIT [V] |
| Open-Dispatch | https://github.com/Matthew-Selvam/Open-Dispatch | `Tools\Open-Dispatch` | `pyproject` 0.5.0; HEAD `832fd54ceee29b468823bd561f8a75328703a466` (2026-11-11); `/healthz` reports 0.5.0 | MIT [V] |
| REDIEU Z Pipeline | **Not a git repository** (custom code written in this project) | `Pipeline\` | n/a — `worker.py`, `ctl.py`, `scripts.json`, `queue.json`, plus discovery files added later | n/a |
| This documentation repo | https://github.com/ueiider/REDIEU-Z-Content-Automation | `REDIEU-Z-Content-Automation\` | base commit `cdd317d` on `main` | — |

Other tools observed: Python 3.12.10 (system), FFmpeg 9.0.2 (gyan.dev full build) and ffprobe, yt-dlp (WinGet install; path referenced in `Pipeline\discover_gta6.py`), Ollama 0.40.15 (Windows app, API `127.0.0.1:11434`).

### Local LLMs actually installed (`ollama list`, 2026-11-12)
`gemma4-16k:latest`, `gemma4:12b`, `qwen3-8b-16k:latest`.
**No Nemotron model is installed in Ollama.** The earlier project docs say "Nemotron intended"; the only Nemotron artefact found is the analysis JSON in `06_Scripts_Voice\`. Which model produced it, and where it ran, is **[P]**. OpenCode configuration was not inspected **[P]**.

---

## 2. MoneyPrinterTurbo (MPT)

**What it is [D+V]:** All-in-one short-video generator: topic → LLM script → footage matching → TTS → subtitles → BGM → render. FastAPI backend + Streamlit WebUI + CLI.

**Python / runtime [V]:** `requires-python >=3.11`, `.python-version` 3.11; local venv `Tools\MoneyPrinterTurbo\.venv`. The REDIEU Z Pipeline borrows this venv's interpreter because it already contains `edge-tts`.

**Key pinned dependencies (pyproject) [V]:** moviepy 2.2.1, streamlit 1.66.1, fastapi 0.136.3, uvicorn 0.32.1, openai 2.24.0, faster-whisper 1.1.0, **edge-tts 7.3.1**, imageio-ffmpeg 0.6.0, pydub 0.25.1, loguru, requests, redis (optional), azure-cognitiveservices-speech, dashscope. Lock file: `uv.lock`.

**Entry points [V]**
| Purpose | Command (from README/source) |
|---|---|
| WebUI | `webui.bat` (Windows) or `mpt webui` |
| REST API + Swagger | `python main.py` (listens per `config.toml`: `0.0.0.0:8080`) |
| CLI | `python cli.py --video-subject "…"` (also `--video-script`, `--video-source`, `--voice-name`, `--bgm-type`, `--bgm-file`, `--bgm-volume`) |

**REST routes [V]:** `POST /videos`, `/subtitle`, `/audio`; `GET /tasks`, task query/delete, stream/download, plus LLM helper routes.

**Providers (config keys present in `config.toml`; values NOT inspected) [V]**
- LLM: dozens of OpenAI-compatible providers, `ollama_base_url = http://127.0.0.1:11434/v1` (model name currently empty), and Claude Code / Codex / ChatGPT / Kimi Code bridges. Active `llm_provider = "openai"`; whether an API key is set **[P]** (not checked, to avoid touching secrets). To stay free/local it would need `llm_provider = ollama` and a model name.
- Footage: `video_source = "local"`; `material_directory` empty. Other options: Pexels, Pixabay, Coverr, generative video providers.
- TTS: `tts_server = "azure-tts-v1"`, voice `en-AU-NatashaNeural-Female`. `app/services/voice.py` imports `edge_tts`, so the v1 route is the free Edge route (label-to-Edge mapping inferred). Other TTS: Azure Speech, SiliconFlow, MiniMax, ElevenLabs, Kokoro, Chatterbox, Fish Audio, VoxCPM.
- Subtitles: `subtitle_provider = "edge"` (alternative: Whisper `large-v3`, cpu/int8).
- Music: `bgm_type = "random"` from bundled songs; ElevenLabs/Sonilo generative music keys exist.
- Aspect: `video_aspect_local = 9:16`.
- **Publishing hook [V]:** `app/services/upload_post.py` cross-posts finished videos to TikTok/Instagram/YouTube via the third-party **Upload-Post** relay. `upload_post_enabled = false`, `upload_post_auto_upload = false` currently.

**Tests:** 265 Python files under `test\` [V count]; not executed.

**Local state [V]:** `config.toml` exists (contains credential fields — never commit). `storage\tasks` and `storage\auth` exist. No MPT server was listening on 8080 during the audit.

**Relevance to REDIEU Z:** Highest-value reusable parts are footage-to-script matching (`match_materials_to_script`, TwelveLabs rerank — paid), subtitle shaping/animation and BGM handling. Its stock sources do not contain GTA 6 gameplay, so `video_source = local` with a curated, licensed library is the only compliant route.

---

## 3. PurffleShorts

**What it is [D+V]:** Python package + CLI "AI YouTube Shorts generator and upload autopilot": LLM script (with self-review), free Edge neural voices, word-synced captions, SFX, ffmpeg render, **YouTube upload/scheduling, Instagram Reels direct upload, other networks through Upload-Post**, local Studio dashboard, MCP server, podcast clipper.

**Runtime [V]:** `requires-python >=3.10`; own `.venv`. Dependencies: requests, python-dotenv, Pillow, edge-tts>=7.0, imageio-ffmpeg, **google-api-python-client, google-auth, google-auth-oauthlib**, anthropic. Extras: `whisper`, `clip`, `face`, `kokoro`, `coqui`.

**Entry points [V]:** console script `purffle-shorts` (`purffle_shorts.cli:main`), `python -m purffle_shorts`, legacy `python YT.py`. Sub-commands in `cli.py`: `run`, `make`, `clip`, `plan`, `ideas`, `stats`, `mcp`, `demo`, `upload`, `history`, `voices`, `studio` (plus setup/doctor helpers).

**Configuration keys [V from `.env.example`; real `.env` NOT read]:** LLM provider/model (OpenAI, Anthropic, Gemini, Groq, OpenRouter, DeepSeek, Mistral, Together, xAI, Ollama via `OLLAMA_HOST`), visuals (`VISUAL_SOURCES`, `MEDIA_DIR`, `BACKGROUND_VIDEO`, `BACKGROUND_LAYOUT`), captions (`CAPTION_*`), `WATERMARK`, `END_CTA`, music (`MUSIC_DIR`, `MUSIC_FILE`, `MUSIC_VOLUME`, `MUSIC_DUCKING`), `SOUND_EFFECTS`, upload (`UPLOAD`, `GOOGLE_CLIENT_SECRETS_FILE`, `YT_TOKEN_FILE`, `YT_PRIVACY`, `PUBLISH_TIMES`, `YT_DAILY_LIMIT`, `SYNTHETIC_MEDIA`, `PUBLISH_TO`, `UPLOAD_POST_API_KEY`, `UPLOAD_POST_USER`, `INSTAGRAM_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_API_VERSION`, `TIKTOK_PRIVACY`), Studio auth (`STUDIO_PASSWORD`, `STUDIO_TOKEN`).

**Modules of interest [V]:** `pipeline.py` (orchestrator), `script.py` (+ review), `tts.py`, `timing.py`, `render.py`, `overlays.py` (captions/emoji), `sfx.py`, `media.py`, `clipper.py`, `youtube.py`, `crosspost.py`, `history.py`, `studio.py`, `mcp_server.py`, `analytics.py`.

**Local state [V]:** `.env` present (not read); `output_videos\` holds earlier sample runs (`script.json`, `metadata.json`, `captions.srt`, `cover.jpg`, `short.mp4`) of unknown origin **[P]**. Working tree clean on `main`.

**Important:** `Pipeline\worker.py` does **not** call PurffleShorts. They share only ideas (Edge TTS, ASS captions, ffmpeg). Earlier docs call PurffleShorts "the existing pipeline"; that is inaccurate for the code that produced Shorts 002+ (see `MASTER_CONTEXT.md`).

**Brand note:** third-party package (publisher branding "Purffle"). REDIEU Z outputs must not carry Purffle Studios branding; if its renderer is ever used, `WATERMARK` must be set to REDIEU Z or disabled **[P: untested]**.

---

## 4. Chopify

**What it is [D+V]:** Local long-video → scored, captioned vertical clips (yt-dlp ingest, faster-whisper, audio+visual scoring, caption styles, SRT, title/description/hashtag JSON, optional Ollama semantic search). Browser dashboard + CLI (`python chopify.py <file|url> --aspect 9:16`, `--action prepare|render`, `--project`, `--search`, `--semantic`).
**Dependencies [V]:** yt-dlp, faster-whisper, opencv-python, numpy (+ ffmpeg).
**Relevance:** Only useful if REDIEU Z owns long recordings (PS5 captures, own VODs). `01_PS5_Recordings` was empty at audit time [V], so Chopify currently has no legitimate input.

---

## 5. Open-Dispatch

**What it is [D+V]:** Self-hosted "one API, many platforms" dispatcher: FastAPI app + dashboard + JSONL on-disk queue + separate scheduler worker with retries; adapters for Bluesky, Discord, Facebook, Instagram, LinkedIn, Telegram, Threads, TikTok, Twitter/X, YouTube.

**Runtime [V]:** Python >=3.11; deps: fastapi, uvicorn, httpx, python-dotenv, tweepy, atproto, jinja2, python-multipart, Pillow (optional: redis, postgres, mcp).

**How it is running now [V]:** `python -m uvicorn api.app:app --host 127.0.0.1 --port 8001` (PID 13476 at audit time). Port 8000 belongs to an unrelated Revit MCP service (PID 59132) and must not be touched. `GET /healthz` → status ok, version 0.5.0, **`worker.running = false`**, queue total 0, `configured_platforms = []` (`.env` defaults are empty; credentials live in a profile — below).

**Entry points [V]:** `uvicorn api.app:app`; `python -m scheduler.worker` or `python cli.py worker`; CLI sub-commands `send`, `queue`, `campaign`, `worker`, `quick-test`, `doctor`; MCP server `mcp_server.py`.

**HTTP API [V]:** `GET /healthz`, `POST /dispatch`, `POST /dispatch/bulk`, `GET /queue`, queue row retry/delete, campaign get/cancel, `POST /ai/adapt`, `GET/POST /profiles…`, `GET /api/profiles`, `GET /media/specs`, `POST /media/transcode` (image specs; Pillow only), plus HTML dashboard routes.

**Credential model [V from `profiles.py`, `scheduler/worker.py`]**
1. Each adapter reads credentials from environment variables, optionally with an `_<ACCOUNT>` suffix.
2. A *profile* (JSON file `profiles.json` in `$OPEN_DISPATCH_DATA`, default `~\.open-dispatch`, stored **in plaintext**) maps per-platform fields to those variables; the worker temporarily injects them (`profile_env`) when the queued unit carries a `profile_id`.
3. If no `profile_id` is supplied, the adapter falls back to `.env`, which is empty for YouTube → publish fails with "missing credentials".

**Profile state [V: key names and set/empty only]:** one profile, id `b8056c7c`, name `REDIEU Z`; platform entries present: **only `youtube`**, with `client_id`, `client_secret`, `refresh_token` all non-empty. No Instagram, TikTok or Facebook credentials exist anywhere in Open-Dispatch configuration. A backup `profiles.json.backup_20261112_203226` exists in the data directory (made by someone else during the session).

**Media rule [V]:** `OPEN_DISPATCH_MEDIA_DIR = D:\GTA6_Content\Tools\Open-Dispatch\media`. Because it is set, adapters call `resolve_media_path(..., strict_root=True)`, which **rejects absolute paths** and anything outside that directory. A `video_path` must be *relative to the media root* (e.g. `incoming/GTA6_Short_002.mp4`). Copies of Shorts were observed in `media\incoming\` (untracked in Open-Dispatch's git; created by another actor, not by this audit). `Ready_For_Review` is not the media root.

**API protection [V]:** `OPEN_DISPATCH_API_TOKEN` is optional and off by default per README; the service is bound to 127.0.0.1 only.

**Git state [V]:** only `?? media/incoming/` is untracked; otherwise clean.
