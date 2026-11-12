# Current Status

Last documented: 2026-11-12

## Project
REDIEU Z GTA 6 Content Automation.

## Local path
`D:\GTA6_Content`

## Production
- Existing pipeline identified.
- Shorts 002–008 observed completed.
- Short 009 observed pending.
- Output directory established.
- Visual relevance needs improvement.

## AI
- OpenCode selected.
- Nemotron/Ollama intended for local analysis and generation.
- Actual active model must be verified.

## Tools
- PurffleShorts: existing pipeline component.
- MoneyPrinterTurbo: installed, requires detailed audit.
- Open-Dispatch: dashboard accessible on port 8001.
- FFmpeg: used by rendering workflow.
- Edge TTS: used by initial rendering workflow.

## YouTube
- Google Cloud project created.
- YouTube Data API v3 enabled.
- OAuth desktop client created.
- google-auth-oauthlib installed.
- OAuth flow completed.
- Local refresh token verified present.
- Open-Dispatch publishing integration not yet proven.

## Publishing
- REDIEU Z profile created.
- Facebook, Instagram, TikTok and YouTube were selected in Compose.
- Actual platform authentication remains to be validated.

## Security
- Secrets stored locally under `D:\GTA6_Content\Secrets`.
- No secret values belong in GitHub.

## Immediate next action
Validate YouTube OAuth integration inside Open-Dispatch and perform one controlled test upload.
