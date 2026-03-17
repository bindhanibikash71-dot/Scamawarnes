import os
import logging
import re
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ChatMemberHandler
)
from database import init_db, add_scammer, remove_scammer, is_scammer, get_scammers

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Helper: Check if user is Admin
async def is_admin(update: Update):
    if update.effective_chat.type == constants.ChatType.PRIVATE:
        return True
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]

# 1. /scam Command
async def scam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to the scammer's message with /scam")
        return

    target = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    await add_scammer(target.id, target.username, target.first_name, chat_id)

    mention = f"@{target.username}" if target.username else target.first_name
    alert_msg = (
        "🚨 SCAM ALERT 🚨\n"
        "━━━━━━━━━━━━━━\n"
        f"💀 {mention}\n"
        "⚠️ Known Scammer\n"
        "🚫 Do not trade\n"
        "━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(alert_msg)

# 2. /unscam Command
async def unscam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to the user's message with /unscam")
        return

    target = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    await remove_scammer(target.id, chat_id)
    await update.message.reply_text(f"✅ User {target.first_name} has been removed from the scam list.")

# 3. /scamlist Command
async def scamlist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    scammers = await get_scammers(chat_id)

    if not scammers:
        await update.message.reply_text("✅ No scammers found in this group database.")
        return

    text = "⚠️🚨 SCAMMER LIST 🚨⚠️\n━━━━━━━━━━━━━━\n"
    for username, first_name in scammers:
        mention = f"@{username}" if username else first_name
        text += f"💀 {mention} — Scammer\n"
    text += "━━━━━━━━━━━━━━"
    
    await update.message.reply_text(text)

# 4. Global Message Monitor (Scam check & Anti-link)
async def monitor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.is_bot:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text or ""

    # Check if user is a marked scammer
    if await is_scammer(user_id, chat_id):
        warning = (
            "🚨 WARNING 🚨\n"
            "⚠️ This user is marked as a scammer.\n"
            "🚫 Be careful before doing any trade."
        )
        await update.message.reply_text(warning)

    # Anti-link Protection (Only for non-admins)
    if not await is_admin(update):
        if re.search(r'(https?://\S+|www\.\S+|t\.me/\S+)', text):
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id, 
                    f"🚫 {update.effective_user.first_name}, links are not allowed in this group!"
                )
            except Exception as e:
                logger.error(f"Failed to delete link: {e}")

# 5. Welcome Message
async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text("🤖 Scam Alert Bot Active! Make me an Admin to protect the group.")
        else:
            welcome = (
                f"👋 Welcome {member.first_name} to the group!\n\n"
                "🛡️ This group is protected by Scam Alert Bot.\n"
                "⚠️ Be cautious of DMs and unsolicited offers."
            )
            await update.message.reply_text(welcome)

if __name__ == '__main__':
    import asyncio

    async def main():
        # Initialize DB
        await init_db()

        # Build App
        app = ApplicationBuilder().token(TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler("scam", scam_handler))
        app.add_handler(CommandHandler("unscam", unscam_handler))
        app.add_handler(CommandHandler("scamlist", scamlist_handler))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_handler))

        logger.info("Bot started...")
        await app.run_polling()

    asyncio.run(main())
