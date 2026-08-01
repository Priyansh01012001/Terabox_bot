import os
import threading
import logging
import asyncio
import yt_dlp
from flask import Flask
from pyrogram import Client, filters

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxBot")

app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Heavy Terabox Bot is active and running!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# Background Flask Thread for Render Port Binding
threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "terabox_heavy_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "🚀 **Heavy Terabox Bot Online!**\n\n"
        "TeraBox ka link bhejo, high-speed extraction shuru karte hain."
    )

@app.on_message(filters.text & ~filters.command("start"))
async def process_terabox_link(client, message):
    url_text = message.text.strip()
    
    if not any(domain in url_text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        await message.reply_text("⚠️ Kripya ek valid TeraBox sharing link bhejiye.")
        return

    status_msg = await message.reply_text("⚙️ **Initializing heavy extraction stream...**")
    target_url = url_text.split()[0]
    output_filename = f"media_{message.id}.mp4"

    ydl_options = {
        'format': 'best/bestvideo+bestaudio',
        'outtmpl': output_filename,
        'cookiefile': 'Cookies.txt' if os.path.exists('Cookies.txt') else None,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }

    try:
        await status_msg.edit_text("📥 **Bypassing security & downloading payload...**")
        
        # Run yt-dlp in an async executor to prevent blocking the event loop
        loop = asyncio.get_running_loop()
        def download_task():
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download([target_url])

        await loop.run_in_executor(None, download_task)

        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 2048:
            await status_msg.edit_text("📤 **Uploading high-resolution file to Telegram...**")
            
            await message.reply_video(
                video=output_filename,
                caption="✅ **Heavy Download Complete!** Powered by custom pipeline."
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ **Extraction Failed:** File size too small or link invalid.")

    except Exception as err:
        logger.error(f"Execution Error: {str(err)}")
        await status_msg.edit_text(f"❌ **Critical Error:** `{str(err)[:100]}`")

    finally:
        # Cleanup residual storage files
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except Exception:
                pass

if __name__ == "__main__":
    logger.info("Starting Telegram Bot Client...")
    app.run()
