# YouTube OAuth Integration

## Google Cloud project

Name: REDIEU-Z-Automation

Project ID: redieu-z-automation

API: YouTube Data API v3

## OAuth application
- Google Auth Platform configured.
- Audience: External.
- OAuth client: Desktop application.
- Client name: REDIEU Z Publisher.
- Testing mode was used.

## Local dependency

`google-auth-oauthlib`

Installed successfully in:

`D:\GTA6_Content\Tools\Open-Dispatch\.venv`

## Local secret locations

`D:\GTA6_Content\Secrets\youtube-oauth-client.json`

`D:\GTA6_Content\Secrets\youtube-token.json`

## Observed verification

Both JSON files were valid.

The token file contained:
- Refresh token.
- Access token.
- Expiry information.

## Open-Dispatch expected environment variables

- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN

The adapter source was inspected and these names were confirmed.

## Important integration gap

Open-Dispatch uses its profile credential storage. Determine whether profile credentials or environment defaults are being used in the actual publishing path.

Do not assume that merely storing the OAuth files under Secrets automatically connects them to the profile.

## Required validation

- Refresh token exchange succeeds.
- Channel identity matches the intended REDIEU Z channel.
- Upload scope is available.
- Upload test succeeds.
- Privacy setting is correct.
- Metadata is correct.

## Google testing mode

Only approved test users can authorise an external app in testing mode. Review the current Google Cloud audience and verification requirements before production use.

## Security

Never commit:
- OAuth client JSON.
- Refresh token.
- Access token.
- Client secret.
- Environment files containing credentials.
