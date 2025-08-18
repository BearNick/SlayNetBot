
# VPN Outline Telegram Bot

A Telegram bot (aiogram 3.x) that sells time-limited Shadowsocks/Outline access keys.
- Generates per-user **ss://** links that auto-import in Outline Client.
- Keys are valid **30 days** by default. On day 31, the user can generate a **new key** after renewing.
- Default tier allows **up to 2 devices** (approximated as 2 concurrent connections).
- Higher tiers: **3–5**, **5–7**, **7–10** devices with different pricing.
- Supports paying for multiple months up-front (configurable). No auto-renew; the user regenerates a new key each month after payment.

> ⚠️ **Legal & distribution notes**
> - iOS apps can only be installed via the App Store. You cannot legally “send the app” inside Telegram for iOS.
> - Android APK sideloading is possible but may violate store/OS policies and is a security risk. The safest option is to give **store links** (which open the store app, not a browser). This repo uses official store links.
> - Outline Manager’s access-key API supports data caps and deletion, but **does not natively enforce “device count.”** We approximate device limits via concurrent connections/IP heuristics and fair-use policy. True device enforcement requires a custom proxy layer or deep server tuning; see `scripts/device_limit_notes.md`.

## Quick start

1. **Create `.env` from template**:
   ```bash
   cp .env.example .env
   ```

2. **Fill required env vars** in `.env`:
   - `BOT_TOKEN` — Telegram bot token.
   - `OUTLINE_API_URL` — e.g. `https://YOUR_SERVER:PORT/` (manager API URL).
   - `OUTLINE_API_KEY` — Outline Manager API key.
   - Optional pricing overrides.

3. **Install deps (Python 3.10+)**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run bot**
   ```bash
   python -m app.bot
   ```

5. (Optional) **Set up daily cleanup** of expired keys:
   ```bash
   bash scripts/create_expired_cleanup_cron.sh
   ```

## Pricing & Plans

Defaults (override in `.env`):

| Tier | Devices | Monthly Price |
|-----:|:-------:|--------------:|
| T2   | up to 2 | 7.00 USD      |
| T5   | 3–5     | 12.00 USD     |
| T7   | 5–7     | 16.00 USD     |
| T10  | 7–10    | 22.00 USD     |

Allowed prepaid months: 1–6 (configurable).

## How it works

- On successful payment, the bot calls Outline Manager API to **create an access key** for the user with:
  - **30-day expiry** (tracked in SQLite).
  - Optional **data cap** (if configured).
- The bot delivers a **tap-to-import** `ss://...` link and quick buttons to install Outline Client on iOS/Android/Desktop.
- On expiry or plan change, the bot **deletes** the old key and can create a new one after the next payment.
- “2 devices” is a **policy** backed by limits on concurrent connections where feasible and by fair-use monitoring. See notes in `scripts/device_limit_notes.md`.

## Commands (user)

- `/start` — start and show plans.
- `Purchase` — choose plan & months → pay → receive key.
- `My Key` — see current key status, days left, regenerate if eligible.
- `Install App` — buttons for iOS / Android / Desktop clients.
- `Help` — FAQ, terms.

## Admin

- Manual revoke/regenerate, user lookup by @username or ID.
- Edit prices and months via env or simple admin commands (stubbed).

## DISCLAIMER

This code is provided for educational purposes. You are responsible for compliance with your local laws, app-store policies, hosting provider terms, and Telegram platform rules.
