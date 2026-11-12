# Commands and Setup Procedures

Audit date: 2026-11-12. Windows 11, PowerShell 5.1 primary shell.
**[OBSERVED]** = the command, process or output was seen working on this machine (by this audit or in logs). **[SOURCE]** = taken from README/source of the tool and **not executed** by this audit. Do not run [SOURCE] commands on a machine other than the audited one without checking paths.
This audit started and stopped nothing.

---

## 1. REDIEU Z Pipeline (`D:\GTA6_Content\Pipeline`)

Interpreter: the existing MoneyPrinterTurbo venv, which already has `edge-tts` (`D:\GTA6_Content\Tools\MoneyPrinterTurbo\.venv\Scripts\python.exe`). FFmpeg/ffprobe must be on `PATH`.

```powershell
# status of worker + queue + last log lines           [OBSERVED]
python D:\GTA6_Content\Pipeline\ctl.py status

# start the detached sequential worker                 [OBSERVED earlier in the session]
python D:\GTA6_Content\Pipeline\ctl.py start

# stop worker (kills its ffmpeg children, re-queues "rendering")   [OBSERVED earlier]
python D:\GTA6_Content\Pipeline\ctl.py stop

# render exactly one pending item in the foreground    [OBSERVED earlier]
D:\GTA6_Content\Tools\MoneyPrinterTurbo\.venv\Scripts\python.exe D:\GTA6_Content\Pipeline\worker.py --once

# render one specific pending item (supported flag in source)       [SOURCE]
...\python.exe D:\GTA6_Content\Pipeline\worker.py --only GTA6_Short_011

# YouTube metadata discovery (no downloads), per script docstring   [SOURCE; file exists, produced discovered_videos.json]
python.exe D:\GTA6_Content\Pipeline\discover_gta6.py
```
Adding a Short: append an object to `Pipeline\scripts.json` (schema in `ARCHITECTURE_AND_DATA_FLOW.md`), then run `ctl.py start`; the worker seeds new ids into `queue.json` as `pending`. Voice total must fall within 25–45 s.

Files: queue `Pipeline\queue.json`, human status `Pipeline\STATUS.md`, logs `Pipeline\logs\`, outputs `D:\GTA6_Content\03_Shorts\Ready_For_Review\`.

## 2. Open-Dispatch (`Tools\Open-Dispatch`)

Observed process: `python -m uvicorn api.app:app --host 127.0.0.1 --port 8001` (dashboard `http://127.0.0.1:8001/`) **[OBSERVED]**; `GET http://127.0.0.1:8001/healthz` **[OBSERVED]** (worker `running:false` at audit time).

From README/CLI source **[SOURCE, not executed]**:
```powershell
cd D:\GTA6_Content\Tools\Open-Dispatch
python -m scheduler.worker          # or: python cli.py worker   — required for queued posts to be sent
python cli.py doctor                # diagnose credentials, data dir, server, worker
python cli.py queue                 # list queue rows
```
Config: `.env` (copy of `.env.example`), data dir `$OPEN_DISPATCH_DATA` (default `~\.open-dispatch`: `profiles.json`, queue JSONL, `.worker_heartbeat`), media root `OPEN_DISPATCH_MEDIA_DIR`.
Port rule: 8000 is the Revit MCP service — never use or stop it.

## 3. MoneyPrinterTurbo (`Tools\MoneyPrinterTurbo`) — **[SOURCE]**
```powershell
cd D:\GTA6_Content\Tools\MoneyPrinterTurbo
.\webui.bat                                   # Streamlit WebUI
python main.py                                # REST API (config.toml: 0.0.0.0:8080 — change to 127.0.0.1 first)
python cli.py --video-subject "…" --video-source local
```
Edit `config.toml` (never commit it). For a free local stack set `llm_provider = "ollama"` and `ollama_model_name` (e.g. a model from `ollama list`).

## 4. PurffleShorts (`Tools\PurffleShorts`) — **[SOURCE]**
```powershell
cd D:\GTA6_Content\Tools\PurffleShorts
.\.venv\Scripts\purffle-shorts.exe --help      # console script defined in pyproject
.\.venv\Scripts\python.exe -m purffle_shorts demo      # keyless sample render
.\.venv\Scripts\python.exe -m purffle_shorts make --script path\to\script.json
.\.venv\Scripts\python.exe -m purffle_shorts upload --id N   # publishes! requires approval — do not run without it
```
Config: `.env` from `.env.example`. YouTube auth would use `GOOGLE_CLIENT_SECRETS_FILE` / `YT_TOKEN_FILE`.

## 5. Chopify (`Tools\Chopify`) — **[SOURCE]**
```powershell
python chopify.py --version
python chopify.py "C:\path\to\own_recording.mp4" --aspect 9:16
python chopify.py --project work --action render --clips 1,3
```

## 6. Local AI and media tools
```powershell
ollama list                      # [OBSERVED] gemma4-16k, gemma4:12b, qwen3-8b-16k (no Nemotron)
ffmpeg -version                  # [OBSERVED] 9.0.2 full build
ffprobe -v error -show_entries stream=width,height,r_frame_rate -of csv=p=0 <video.mp4>   # [OBSERVED pattern]
```

## 7. Secrets and one-time YouTube authorisation (documented, do not repeat unnecessarily)
- Files: `D:\GTA6_Content\Secrets\youtube-oauth-client.json`, `youtube-token.json`, helper scripts `youtube_oauth_setup.py`, `validate_youtube.py`.
- Re-authorisation, if the token expires (Testing mode ≈ 7 days [E]) or a wider scope is needed, is a **human action**: run `youtube_oauth_setup.py` in the venv that has `google-auth-oauthlib` (`Tools\Open-Dispatch\.venv`), sign in to the REDIEU Z Google account in the browser, then update the Open-Dispatch profile through its dashboard (`/profiles`). Never paste secret values into chat, docs, tickets or commits.

## 8. Git (this documentation repo)
```powershell
cd D:\GTA6_Content\REDIEU-Z-Content-Automation
git status -sb ; git log --oneline -5
git diff --cached --name-only        # inspect before every commit: no *.json credentials, no media, no .env
```
Remote `origin` = `https://github.com/ueiider/REDIEU-Z-Content-Automation.git`. Pushing requires owner approval.
