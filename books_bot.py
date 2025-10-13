import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable (recommended)
TOKEN = os.getenv("BOT_TOKEN")

# --- Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\nWelcome to the Student Book Finder Bot 📚.\n"
        "Send me a keyword or your grade, and I’ll help you find books or notes!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when /help is issued."""
    await update.message.reply_text(
        "Here’s what I can do:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/menu - Show main menu\n"
        "\nYou can also just send text and I’ll respond!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle normal user messages."""
    text = update.message.text.strip().lower()
    logger.info(f"Received message: {text}")
    await update.message.reply_text(
        f"You said: {text}\n\n(Feature: This is where your bot logic will go!)"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors and exceptions."""
    logger.error(f"Exception while handling an update: {context.error}")


# --- Main Execution ---

if __name__ == "__main__":
    logger.info("Starting bot using webhook mode...")

    async def main():
        # Create bot app
        app = (
            Application.builder()
            .token(TOKEN)
            .read_timeout(120.0)
            .write_timeout(120.0)
            .build()
        )

        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("menu", start_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_error_handler(error_handler)

        # Delete any existing webhook to avoid conflicts
        await app.bot.delete_webhook(drop_pending_updates=True)

        # Webhook setup
        hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        port = int(os.environ.get("PORT", 10000))
        webhook_url = f"https://{hostname}/webhook"

        logger.info(f"Setting webhook to {webhook_url}")

        await app.bot.set_webhook(url=webhook_url)

        # Start webhook server
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=webhook_url
        )

        logger.info(f"Webhook started on port {port}")
        await app.updater.idle()

    asyncio.run(main())
