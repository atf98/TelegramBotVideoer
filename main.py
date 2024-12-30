from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
from datetime import datetime

# Retrieve bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found. Please set it as an environment variable.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    await update.message.reply_text("Hello! Send me a video link, and I'll download it for you.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for processing video download links."""
    url = update.message.text
    try:
        await update.message.reply_text("Downloading video, please wait...")

        # Prepare file name with date, time, and title
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{timestamp}_%(title).50s.%(ext)s',  # Save with timestamp and first 50 characters of title
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)  # Get the generated file name

        # Send the downloaded video
        with open(file_name, 'rb') as video:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video)

        # Clean up the downloaded file
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f"Failed to download video: {e}")

def main():
    """Main function to start the bot."""
    # Create the Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
