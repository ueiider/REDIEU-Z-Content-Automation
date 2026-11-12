# REDIEU Z — Project History

This document records the available conversation history and verified operational observations. Unknown details are explicitly identified rather than invented.

## Phase 1 — Initial content research

The project began with the objective of finding:
- Viral GTA 6 videos.
- Gameplay footage and gameplay demonstrations.
- Official trailers.
- GTA 6 news and analysis.
- GitHub repositories that automate Shorts.
- Free sources of usable video footage.
- AI tools capable of generating narration, captions and descriptions.

The intention was to analyse successful content and create original English videos rather than simply repost other creators' work.

## Phase 2 — Initial production pipeline

Local project created:

`D:\GTA6_Content`

An existing production workflow was identified involving:
- Pipeline directory.
- PurffleShorts.
- yt-dlp.
- JSON-based scripts and queue.
- FFmpeg.
- Edge TTS.
- Animated captions.
- REDIEU Z branding.

The explicit instruction was to build on existing components, not reinstall or recreate working tools.

## Phase 3 — Original GTA 6 Shorts

A production specification was created to:
1. Discover 30 GTA 6 videos.
2. Collect title, channel, URL, views, duration and publication date.
3. Rank by popularity and views per day.
4. Analyse available transcripts using Nemotron.
5. Identify 10 promising topics.
6. Generate five original English scripts.
7. Include hooks, narration, captions, titles, descriptions and hashtags.
8. Label confirmed facts and rumours.
9. Render a test Short.
10. Use original or properly licensed footage.

## Phase 4 — Production queue

The queue used:

- `Pipeline/ctl.py`
- `Pipeline/worker.py`
- `scripts.json`
- `queue.json`
- `Pipeline/logs/production.log`

A worker was started in the background.

Observed status on 12 November 2026:

| Video | Observed state |
|---|---|
| GTA6_Short_002 | Completed |
| GTA6_Short_003 | Completed |
| GTA6_Short_004 | Completed |
| GTA6_Short_005 | Completed |
| GTA6_Short_006 | Completed |
| GTA6_Short_007 | Completed |
| GTA6_Short_008 | Completed |
| GTA6_Short_009 | Pending |

The earlier production run had six completed, one rendering and one pending. The worker was stopped with `ctl.py stop`.

A later status confirmed seven completed and one pending.

Known output directory:

`D:\GTA6_Content\03_Shorts\Ready_For_Review`

Expected output included MP4 videos and accompanying JSON metadata.

## Phase 5 — Initial video review

The generated videos were not yet considered publication-ready.

Problems identified:
- Visuals did not always match the narration.
- The pipeline relied heavily on trailer footage.
- More genuine gameplay footage options were required.
- The content needed to be more closely connected to actual GTA 6 information.
- Background music needed evaluation.
- Watermark placement needed improvement.

Important user requirements:
- Every visual must support the spoken subject.
- Use varied gameplay and relevant footage.
- Include suitable background music where appropriate.
- Use animated captions.
- Use `@REDIEUZ` watermark.
- Position watermark away from the top because other accounts may crop and repost the video.
- Maintain original branding.

## Phase 6 — Production tools

The user decided to use OpenCode with Nemotron rather than depend on Claude.

The objective is to use local AI models through Ollama wherever possible.

Existing production components must be inspected before modification.

## Phase 7 — MoneyPrinterTurbo

MoneyPrinterTurbo was installed as part of the production-tool investigation.

The user wanted to explore its capabilities and use the useful functions instead of relying exclusively on a custom pipeline.

Its exact installed version, configuration, model provider and production status must be checked locally.

## Phase 8 — Open-Dispatch

Open-Dispatch was installed at:

`D:\GTA6_Content\Tools\Open-Dispatch`

Version observed in the dashboard: `v0.5.0`.

The application was initially tested on port 8000. This failed because port 8000 was already occupied by the Revit MCP HTTP server.

The Revit MCP process was identified as:
- Process: `python.exe`
- Command: `main.py --http`
- PID observed: 59132
- Port: 8000

Open-Dispatch was subsequently accessed successfully on:

`http://127.0.0.1:8001`

Do not take over or terminate the Revit MCP service.

## Phase 9 — REDIEU Z publishing profile

A profile was created in Open-Dispatch.

Profile name observed in Compose:

`RZ_REDIEU_Z (no creds)`

Another displayed name was `REDIEU Z`.

The profile initially had no platform credentials.

Platform selections tested:
- Facebook.
- Instagram.
- TikTok.
- YouTube.

The dashboard allows multiple platform selection, captions, YouTube video path, title, visibility and optional scheduling.

Credentials are stored by Open-Dispatch in its profile storage. The local storage security must be reviewed.

## Phase 10 — Google Cloud and YouTube API

Google Cloud project created:

`REDIEU-Z-Automation`

Project ID:

`redieu-z-automation`

YouTube Data API v3 was enabled.

Google required multi-factor authentication before allowing Cloud Console access. This was completed.

Google Auth Platform was configured.
- Audience: External.
- OAuth application created.
- OAuth client type: Desktop app.
- Client name: REDIEU Z Publisher.

The application was in testing mode, so the authorising Google account needed to be an approved test user.

An initial access-denied screen showed that the app had not completed Google verification. The browser subsequently reported:

`The authentication flow has completed. You may close this window.`

## Phase 11 — OAuth dependencies and credentials

The following dependency was installed in the Open-Dispatch virtual environment:

`google-auth-oauthlib`

Installation and import verification succeeded.

Virtual environment:

`D:\GTA6_Content\Tools\Open-Dispatch\.venv`

OAuth JSON source was located in the user's Desktop/OneDrive Desktop location.

Credential files were then created under:

`D:\GTA6_Content\Secrets`

Expected files:
- `youtube-oauth-client.json`
- `youtube-token.json`

A PowerShell verification confirmed:
- Both files contained valid JSON.
- Refresh token present.
- Access token present.
- Expiry field present.

Actual credential values were deliberately not recorded in this document.

## Current state at handover

The YouTube OAuth authorisation flow has completed and a refresh token exists locally.

This does NOT yet prove that Open-Dispatch can successfully publish a video.

The next step is to validate the token, connect the credentials to the REDIEU Z profile and perform a controlled private/unlisted test upload before enabling public publishing.

All states must be rechecked on the local machine.
