# Open-Dispatch Integration

## Installation
`D:\GTA6_Content\Tools\Open-Dispatch`

## Dashboard
`http://127.0.0.1:8001`

## Observed version
v0.5.0

## Port conflict
Port 8000 belongs to the existing Revit MCP HTTP service. Open-Dispatch must use port 8001 unless the local configuration is deliberately changed.

## Profile
REDIEU Z publishing profile was created.

## Compose capabilities observed
- Multiple platform selection.
- Caption text.
- YouTube video file path.
- Optional title.
- Visibility selection.
- Optional scheduling.
- Optional webhook.
- AI text adaptation preview.
- Advanced raw JSON format.

## Platforms displayed
Bluesky, Discord, Facebook, Instagram, LinkedIn, Telegram, Threads, TikTok, Twitter and YouTube.

## Publishing status
The dashboard was accessible and the profile was created.

The actual authentication and publishing integrations still require individual validation.

## Required next steps

1. Inspect the local Open-Dispatch configuration.
2. Connect YouTube OAuth credentials to the profile.
3. Confirm the profile's stored credentials.
4. Test token refresh.
5. Verify YouTube channel identity.
6. Upload one test video privately or unlisted.
7. Confirm returned video ID and URL.
8. Test scheduling.
9. Inspect Instagram, TikTok and Facebook requirements separately.

Never assume that selecting a platform means its credentials are configured.
