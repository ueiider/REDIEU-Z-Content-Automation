# Progress Tracker — Verified Snapshot 2026-11-12

Supersedes the status column of `PROGRESS_TRACKER.md` (left unchanged for history). Every row was checked against live files/processes at the time of the audit; "Evidence" says how. Re-verify before relying on it — the production workflow was still changing while this was written.

## Verified completed
| Item | Evidence |
|---|---|
| Sequential render pipeline (`Pipeline\worker.py`, `ctl.py`) exists and renders 1080×1920 / 30 fps Shorts with Edge TTS, ASS captions, SFX and REDIEU Z mark | source read; `production.log`; files in `Ready_For_Review` |
| Persistent queue with pending/rendering/completed/failed and one retry | `queue.json` structure; `MAX_ATTEMPTS=2` |
| 8 videos rendered: `GTA6_Short_002–008`, `010` (each MP4 + sidecar JSON, status `NEEDS_HUMAN_REVIEW`) | `queue.json` + directory listing |
| Detached background start/stop/status tooling | `ctl.py` source; worker observed running independently earlier |
| YouTube Data API OAuth completed locally; token + client files present; scope `youtube.upload` | `Secrets\` file structure (keys only) |
| Open-Dispatch v0.5.0 running on `127.0.0.1:8001`; profile `REDIEU Z` exists with YouTube credential fields populated | `/healthz`; listener check; `profiles.json` structure (set/empty only) |
| YouTube discovery (metadata only) produced `discovered_videos.json`, `topics.json`, `discovery_queue.json` | files present in `Pipeline\` (written by the main workflow) |
| Technical audit and documentation set | `11_Audit\` (this branch) |

## Verified pending / failed
| Item | State | Evidence |
|---|---|---|
| `GTA6_Short_009` | **failed** — "interrupted render: worker stopped before completion"; no MP4 | `queue.json` |
| `GTA6_Short_011–014` | pending | `queue.json` |
| Render worker | **not running** at audit time | `ctl.py status` |
| Open-Dispatch scheduler worker | **not running** | `/healthz` `worker.running=false` |
| YouTube publishing | **never tested** — no upload attempted, no video ID | empty queue; no publication log |
| YouTube channel identity | unverified (upload-only scope vs `channels.list`) | token scopes; `validate_youtube.py` source |
| Instagram, Facebook, TikTok | **no credentials, no tests** | `.env` empty; profile has only `youtube` |
| Narration-matched visuals | not implemented (arbitrary cuts of one local trailer file) | `worker.py` |
| Rights-cleared footage | none | `footage_note` in sidecars; `01_PS5_Recordings` empty |
| Background music | not implemented | `worker.py` |
| Watermark spec (`@REDIEUZ`, away from top) | not met (text `REDIEU Z`, top-right) | `worker.py` style |
| Approval workflow / approval records | not implemented | no code/files |
| Publish bridge (render → Open-Dispatch) | not implemented (manual copies observed in `media\incoming\`) | no code references |
| Nemotron via Ollama | model not installed (gemma4, qwen3 only) | `ollama list` |
| MoneyPrinterTurbo / PurffleShorts comparison | not performed | no outputs |
| MPT LLM key set? PurffleShorts `.env` content? OpenCode config? | **unverified** (deliberately not read) | — |

## Workstream summary
| Workstream | Status now | Next action |
|---|---|---|
| Local pipeline | Working, quality-limited | Phase 0 stabilise, Phase 1 relevance/rights |
| Shorts 002–008, 010 | Completed, awaiting human review | Review; verify each `confirmed` claim with a source |
| Short 009 | Failed (interrupted) | Re-queue after worker stability fix |
| Shorts 011–014 | Pending | Start worker when ready |
| OpenCode/Nemotron | Unverified/absent | Decide model standard |
| MoneyPrinterTurbo | Audited (docs) | Bake-off after Phase 1 |
| PurffleShorts | Audited (docs) | Reuse IG direct upload / scheduling ideas |
| Open-Dispatch | Running, worker off | Start worker; build bridge (Phase 3) |
| YouTube OAuth | Authorised, unproven | Token strategy + private test (Phase 3) |
| Instagram / Facebook / TikTok | Not started | Phases 4–6 |
| Automated dispatch | Not connected | Phase 3 → 7 |
