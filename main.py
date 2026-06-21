import os
import asyncio
import aiohttp
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7936861392:AAFUtSs-mmGRhQfwSfyzttIemFxefBG_qts')
API_KEY = os.environ.get('API_KEY', 'KEY_3FFF98D2_NUMBERA')
API_BASE_URL = 'https://anishexploits.com/api/api.php'

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def format_user_data(data_list):
    """Formats the API JSON response into a readable Telegram message."""
    if not data_list or not isinstance(data_list, list):
        return "❌ No user data found in the response."

    user = data_list[0]
    message = (
        f"🔍 *User Details Found*\n"
        f"──────────────\n"
        f"👤 *Name*: {user.get('name', 'N/A')}\n"
        f"👨 *Father's Name*: {user.get('fname', 'N/A')}\n"
        f"🆔 *Aadhar*: {user.get('aadhar', 'N/A')}\n"
        f"📞 *Phone*: {user.get('num', 'N/A')}\n"
        f"📱 *Alternate*: {user.get('alt', 'N/A')}\n"
        f"📍 *Address*: {user.get('address', 'N/A')}\n"
        f"📡 *Circle*: {user.get('circle', 'N/A')}\n"
        f"──────────────\n"
        f"💳 *Buy API*: @Cyb3rS0ldier"
    )
    return message

async def fetch_user_data(phone_number):
    """Fetches user data from the API asynchronously."""
    params = {
        'key': API_KEY,
        'type': 'number',
        'num': phone_number
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_BASE_URL, params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success' and data.get('result'):
                        return format_user_data(data['result'])
                    else:
                        return f"❌ API Error: {data.get('status', 'Unknown error')}"
                else:
                    return f"❌ HTTP Error: {response.status}"
    except asyncio.TimeoutError:
        return "❌ Request timed out. The API might be slow or down."
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return f"❌ An unexpected error occurred: {str(e)}"

# --- Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "👋 Hello! I'm a User Details Bot.\n\n"
        "Simply send me a phone number (e.g., `6209876775`) and I'll fetch the associated details.\n"
        "Send /help for more info.",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    await update.message.reply_text(
        "📖 *How to use:*\n"
        "1. Send a valid 10-digit phone number.\n"
        "2. Wait a few seconds for the result.\n\n"
        "⚠️ *Note:* This bot uses a third-party API. Data accuracy is not guaranteed.\n"
        "For API access, contact: @Cyb3rS0ldier",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages (phone numbers)."""
    phone_number = update.message.text.strip()
    # Basic validation: remove any spaces and check if it's a 10-digit number
    phone_number = ''.join(filter(str.isdigit, phone_number))
    if len(phone_number) == 10:
        # Send a "typing" action to indicate processing
        await update.message.chat.send_action(action="typing")
        # Fetch and send the formatted result
        result_message = await fetch_user_data(phone_number)
        await update.message.reply_text(result_message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ Please send a valid 10-digit phone number without country code.\n"
            "Example: `6209876775`",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# --- Main Bot Runner ---
def main():
    """Starts the bot."""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("BOT_TOKEN environment variable not set!")
        return

    logger.info("Starting bot...")
    
    # Create the Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Register message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    app.add_error_handler(error_handler)

    # Start the bot (using polling)
    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()