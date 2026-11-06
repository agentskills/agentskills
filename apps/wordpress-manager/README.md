# WordPress Manager

Flutter Android starter for managing `getachewnohe31-deujx.wordpress.com` through the WordPress.com API.

## Current status

This is a safe starter scaffold. OAuth sign-in, create/edit/delete operations, media, pages, comments, Android redirect configuration, and release signing still need to be completed before a Play Store release.

## Security

Never commit OAuth client secrets, access tokens, passwords, keystores, or signing credentials. Configure secrets through local environment files or CI/CD secrets.

## Run

```bash
cd apps/wordpress-manager
flutter pub get
flutter run
```

The API client expects an access token in secure storage under `access_token`; the authentication screen and OAuth callback are intentionally not enabled until the WordPress.com OAuth redirect URI is confirmed.
