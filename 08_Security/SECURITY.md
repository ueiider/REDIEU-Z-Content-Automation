# Security Policy

## Never commit
- `.env`
- OAuth JSON.
- Client secrets.
- Refresh tokens.
- Access tokens.
- Passwords.
- Cookies.
- Session files.
- Private account information.
- Private videos or copyrighted media.

## Known local secret directory

`D:\GTA6_Content\Secrets`

## Git protection
Use `.gitignore` and inspect staged files before every commit.

## Required protections

- Keep secrets outside the repository.
- Restrict local folder permissions.
- Do not print tokens in terminal logs.
- Do not include credentials in AI prompts.
- Use GitHub Secrets only for credentials genuinely required by GitHub Actions.
- Rotate exposed credentials immediately.

## Important
OAuth client configuration and refresh tokens are sensitive even when the application is in testing mode.

Do not upload the user's original client_secret JSON to GitHub.
