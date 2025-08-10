# Telegram Admin Bot + Panel (Railway-ready)

## Quick deploy (Railway)
1. Upload this repo to GitHub.
2. Click the **Deploy on Railway** button (or create a new project on Railway and connect this repo).
3. Add environment variables: `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`, `ADMIN_SECRET`.
4. Deploy and wait.

(A deploy button template can be placed here after creating a Railway template.)

## Local dev
1. Copy `.env.example` to `.env` and fill values.
2. python -m venv venv
3. source venv/bin/activate
4. pip install -r requirements.txt
5. python db_init.py
6. python main.py
