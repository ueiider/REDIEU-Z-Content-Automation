# MASTER CONTEXT — REDIEU Z GTA 6 Content Automation

Single-file briefing so another AI (or human) can continue the project without prior conversation.
Snapshot: **2026-11-12**. Tags: **[V]** verified locally, **[P]** pending/unverified, **[E]** external rule to re-check. Details: `11_Audit/`. Intent/history: `01_Project`, `02_History`, `10_AI_Handover`.

---

## 1. What the project is
A free-first, local-first system to produce original English GTA 6 Shorts for the channel **REDIEU Z** (9:16, 1080×1920, 30 fps, about 25–45 s) and, after human approval, publish them to YouTube, Instagram, Facebook and TikTok. Editorial rule: **confirmed Rockstar information must be clearly separated from rumours**; never invent facts. The owner decides everything public. Brand: REDIEU Z (the spec says an `@REDIEUZ` watermark placed away from the top edge — not yet implemented). Do not use Purffle Studios branding.

## 2. Machine layout
```
D:\GTA6_Content
├─ 01_PS5_Recordings        (empty)                      ├─ Pipeline\   custom render pipeline (NOT in git)
├─ 02_Raw_Clips             GTA6_Official_Trailer_2.mp4  ├─ Secrets\    OAuth client/token + helper scripts (NEVER read values / commit)
├─ 03_Shorts\Ready_For_Review   finished MP4 + JSON      ├─ Tools\      MoneyPrinterTurbo, PurffleShorts, Chopify, Open-Dispatch, LosslessCut
├─ 06_Scripts_Voice         transcripts, Nemotron-style analysis JSON, Short_001
└─ REDIEU-Z-Content-Automation   this docs repo (origin github.com/ueiider/REDIEU-Z-Content-Automation)
```
Also at root: older downloaded `.webm` files and `.part` leftovers, yt-dlp logs, `shorts_ai_plan.json`, candidate CSVs. Treat them as third-party media of unknown rights.

## 3. The real data flow today [V]
`topics → Pipeline\scripts.json → Pipeline\worker.py (queue.json) → edge-tts voice + ffmpeg cuts of ONE local trailer file + ASS captions + synthetic SFX → 03_Shorts\Ready_For_Review\ID.mp4 + ID.json (NEEDS_HUMAN_REVIEW)`.
Publishing is a **separate, unconnected** system: Open-Dispatch (`127.0.0.1:8001`) with a `REDIEU Z` profile that holds YouTube credentials only. Nothing automatically moves an approved video into it. Diagram: `11_Audit/ARCHITECTURE_AND_DATA_FLOW.md`.

## 4. Components and the truth about each
| Component | Reality |
|---|---|
| **Pipeline** (`worker.py`, `ctl.py`) | The code that actually produced Shorts 002+. Run-to-empty batch worker, detached via `ctl.py`. Not a git repo. |
| **PurffleShorts** (github.com/Chamanrajragu/purffle-shorts, v3.0.0+13) | Independent third-party tool. **Not used by the Pipeline.** Has YouTube + Instagram direct upload + Upload-Post relay code worth reusing. |
| **MoneyPrinterTurbo** (github.com/harry0703/MoneyPrinterTurbo, v1.3.10+12) | Third-party generator; only its venv interpreter (has `edge-tts`) is borrowed. Has an Upload-Post integration (disabled). |
| **Chopify** (github.com/mehbul/chopify, v1.4.0+5) | Clips long recordings; no legitimate input exists yet. |
| **Open-Dispatch** (github.com/Matthew-Selvam/Open-Dispatch, v0.5.0) | Publisher/queue/dashboard. API running; **scheduler worker not running**. Media must live under `Tools\Open-Dispatch\media\` (relative paths). |
| **Ollama** | Models: gemma4-16k, gemma4:12b, qwen3-8b-16k. **No Nemotron**, despite earlier docs. |

## 5. Pipeline cheat-sheet
```powershell
python D:\GTA6_Content\Pipeline\ctl.py status | start | stop
```
Inputs: `scripts.json` (`id,title,hook_text,description,hashtags,scenes[{tag: hook|confirmed|rumor|cta, text}]`). State: `queue.json` (`pending|rendering|completed|failed`, one retry). Outputs/sidecars: `Ready_For_Review`. Logs: `Pipeline\logs\`. More commands: `11_Audit/COMMANDS_AND_SETUP.md`.
Queue at snapshot: 002–008 and 010 completed; **009 failed (interrupted)**; 011–014 pending; worker idle. The main workflow was still editing the Pipeline while this was written — re-check with `ctl.py status`.

## 6. Publishing state
- **YouTube:** OAuth Desktop client done; token scope = `youtube.upload` only [V]. Open-Dispatch profile `REDIEU Z` (id `b8056c7c`) has client id/secret/refresh token populated (set/empty check only) [V]. **Never test-uploaded** [V]. Channel identity unverified (the validation script needs a read scope — likely fails) [P]. Testing-mode refresh tokens expire in about 7 days and unverified API projects may be restricted to private uploads [E].
- **Instagram / Facebook / TikTok:** no credentials anywhere [V]. Open-Dispatch adapters need **public URLs** (IG `video_url`, FB `file_url`, TikTok `PULL_FROM_URL`) [V]. PurffleShorts can upload to Instagram directly from disk; TikTok/Facebook realistically need either a TikTok API audit or the paid third-party Upload-Post relay. Details: `11_Audit/PUBLISHING_INTEGRATIONS_AUDIT.md`.
- **Danger:** the Open-Dispatch YouTube adapter defaults `privacy` to `public`; always send `private`/`unlisted` in tests.

## 7. Known problems (top ten; full list in `11_Audit/GAPS_BUGS_RISKS.md`)
1. Visuals are arbitrary cuts of a single trailer file — no narration relevance, rights not cleared.
2. No render→publish bridge; no approval record.
3. Open-Dispatch worker off; media-root path restriction.
4. YouTube never tested; scope/identity/token-lifetime issues.
5. Watermark off-spec; no music; caption timing estimated.
6. Pipeline not under version control; queue/stop races; Short 009 failed.
7. `confirmed` claims lack stored citations.
8. Nemotron absent; docs drift (README path case, stale status files).
9. Plaintext secrets in several local files (outside the repo; keep it that way).
10. MoneyPrinterTurbo config listens on 0.0.0.0 if started.

## 8. Roadmap pointer
`09_Roadmap/IMPLEMENTATION_ROADMAP_MULTIPLATFORM.md` (Phases 0–8) and `09_Roadmap/PROGRESS_TRACKER_VERIFIED_2026-11-12.md`. Next concrete steps: Phase 0 stabilise → Phase 1 relevance/rights → Phase 2 QC + approval → Phase 3 YouTube private test via a publish bridge.

## 9. Hard rules for any agent
1. **Never publish/upload** without explicit owner approval; first tests private/unlisted.
2. **Never read, print, log, copy or commit secret values** (`Secrets\`, `.env`, `profiles.json`, `config.toml`, token JSON). Document locations and key names only.
3. **Never stop or touch port 8000 (Revit MCP).** Open-Dispatch is on 8001.
4. Don't delete/overwrite videos, queue entries, or `scripts.json`/`queue.json` while a worker may be running; stop the worker via `ctl.py` and tell the owner.
5. Don't convert assumptions into facts: tag [V]/[P]/[E]; label rumours; no release-date claims without same-day verification.
6. Use original, licensed or explicitly authorised footage only; trailer-derived output is an editing test.
7. Prefer free/local tools; no paid APIs or subscriptions without approval. Don't reinstall working dependencies.
8. Don't modify unrelated projects. Make focused changes; update docs after every verified change.
9. Commit docs on a branch; never push without approval.

## 10. How to continue (first 30 minutes)
1. `git -C D:\GTA6_Content\REDIEU-Z-Content-Automation log --oneline -5`; read this file, then `11_Audit\GAPS_BUGS_RISKS.md`.
2. `python D:\GTA6_Content\Pipeline\ctl.py status`; `curl http://127.0.0.1:8001/healthz`; `ollama list`.
3. Ask the owner for the five decisions in the roadmap's "Decisions needed" list; do not start Phases 3–6 before the owner has approved a footage policy and a test video.
4. Update `PROGRESS_TRACKER_VERIFIED_*` with anything you verify.
