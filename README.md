# Telegram Scam Alert Bot

A production-ready Telegram bot to manage and alert users about scammers in groups.

## Features
- `/scam` (Reply to user): Mark as scammer.
- `/unscam` (Reply to user): Remove mark.
- `/scamlist`: Show all scammers.
- **Auto-Warning**: Triggers if a scammer sends a message.
- **Anti-Link**: Removes links sent by non-admins.
- **Welcome Message**: Greets new members.

## Deployment on Render
1. Create a new **Background Worker** on Render.
2. Connect your GitHub repository.
3. Add Environment Variable:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
4. Render will automatically detect the `Procfile` and start the bot.

## Local Setup
1. `pip install -r requirements.txt`
2. `export TELEGRAM_BOT_TOKEN='your_token_here'`
3. `python bot.py`
