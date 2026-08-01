import os
import threading
import logging
import asyncio
import requests
import yt_dlp
from flask import Flask
from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxBypassBot")

app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Bypass Terabox Bot is active!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "terabox_bypass_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("🚀 **Bypass Terabox Bot Online!** Link bhejo.")

@app.on_message(filters.text & ~filters.command("start"))
async def process_terabox_link(client, message):
    url_text = message.text.strip()
    
    if not any(domain in url_text.lower() for domain in ["terabox", "terashare", "1024tera", "tera", "nephobox"]):
        await message.reply_text("⚠️ Kripya ek valid TeraBox sharing link bhejiye.")
        return

    status_msg = await message.reply_text("⚙️ **Bypassing cloud blocks & downloading...**")
    raw_url = url_text.split()[0]
    output_filename = f"media_{message.id}.mp4"

    try:
        # Advanced headers mimicking a real browser session to bypass cloudflare/terabox blocks
        ydl_options = {
            'format': 'best',
            'outtmpl': output_filename,
            'quiet': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Cookie': 'ndus=YVOf2LVPeHuiSROI62W-_icpi1Ifdv-FV_QuBXQ'
            }
        }
        
        loop = asyncio.get_running_loop()
        def download_task():
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download([raw_url])

        await loop.run_in_executor(None, download_task)

        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 50000:
            await status_msg.edit_text("📤 **Uploading high-resolution file to Telegram...**")
            await message.reply_video(video=output_filename, caption="✅ **Download Successful!**")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ **Blocked:** Render ki IP ko TeraBox block kar raha hai. Yeh link direct cloud par nahi chalega.")

    except Exception as err:
        logger.error(f"Error: {str(err)}")
        await status_msg.edit_text(f"❌ **Error:** `{str(err)[:100]}`")

    finally:
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except Exception:
                pass

if __name__ == "__main__":
    app.run()
