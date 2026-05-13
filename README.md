# BW Weekend Bot (v2)

## Overview
A multi‑platform (Telegram + VK) informational bot that delivers up‑to‑date content about the **BW Weekend** festival. The bot is built with a clean‑architecture, domain‑driven design and a data‑driven content model, allowing non‑technical editors to add or update posts without touching code.

## Features
- **Dual platform support** – separate processes for Telegram (aiogram) and VK (vkbottle).
- **Content as data** – all messages, images, videos and navigation are defined in YAML files under `content/data/`.
- **Progressive release** – each node can have an `available_from` date or feature flag, making content appear automatically at the right time.
- **Stateless business logic** – use‑cases are pure Python functions that do not depend on any framework.
- **Dockerised deployment** – `docker compose up` runs the whole system (Telegram bot, VK bot, Redis).
- **Observability** – rotating logs, Prometheus metrics, and interaction recording.
- **Testing & CI** – full test suite, linting with Ruff, automated documentation generation.

## Quick start (local development)
```bash
# clone the repository
git clone <repo_url>
cd bw-weekend-bot

# create a virtual environment (Python 3.14)
python3.14 -m venv .venv
source .venv/bin/activate

# install dependencies
uv pip install -r requirements.txt

# copy the example env file and fill in your tokens
cp .env.example .env
# edit .env → set BOT_TOKEN_TELEGRAM, BOT_TOKEN_VK, REDIS_URL, etc.

# run the bots locally (polling mode for Telegram, long‑polling for VK)
python main.py --local   # starts the Telegram polling bot
# in another terminal start the VK bot
python src/presentation/entrypoint_vk.py
```

## Docker deployment
```bash
docker compose up -d   # starts telegram_bot, vk_bot, redis
```
The containers read configuration from environment variables; mount a custom `content/data/` directory if you want to override the default content.

## Documentation
- **Architecture** – `docs/architecture.md`
- **API / Use‑cases** – `docs/api.md`
- **User guide** – `docs/user_guide.md`
- Generated site – accessible at `http://localhost:8000` when running `mkdocs serve`.

## License
MIT – see `LICENSE`.
