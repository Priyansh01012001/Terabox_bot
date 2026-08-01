import os
import threading
import logging
import asyncio
import subprocess
import requests
import yt_dlp
from flask import Flask
from pyrogram import Client, filters

# Force upgrade yt-dlp to latest github master to support new terabox domains
subprocess.run(["pip", "install", "--force-reinstall", "https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxProMaxBot")

app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Pro Max Terabox Bot is active and running!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "terabox_promax_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("🚀 **Pro Max Terabox Bot Online with Nightly Engine!** Link bhejo.")

@app.on_message(filters.text & ~filters.command("start"))
async def process_terabox_link(client, message):
    url_text = message.text.strip()
    
    if not any(domain in url_text.lower() for domain in ["terabox", "terashare", "1024tera", "tera", "nephobox", "freedl"]):
        await message.reply_text("⚠️ Kripya ek valid TeraBox sharing link bhejiye.")
        return

    status_msg = await message.reply_text("⚙️ **Resolving URL & pulling via Nightly Engine...**")
    raw_url = url_text.split()[0]
    output_filename = f"media_{message.id}.mp4"

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        })
        
        resp = session.get(raw_url, allow_redirects=True, timeout=20)
        resolved_url = resp.url
        logger.info(f"Resolved Target URL: {resolved_url}")

        ydl_options = {
            'format': 'best/bestvideo+bestaudio',
            'outtmpl': output_filename,
            'cookiefile': 'Cookies.txt' if os.path.exists('Cookies.txt') else None,
            'noplaylist': True,
            'quiet': True,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Cookie': 'ndus=YVOf2LVPeHuiSROI62W-_icpi1Ifdv-FV_QuBXQ'
            }
        }
        
        loop = asyncio.get_running_loop()
        def download_task():
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download([resolved_url])

        await loop.run_in_executor(None, download_task)

        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 2048:
            await status_msg.edit_text("📤 **Uploading high-resolution file to Telegram...**")
            await message.reply_video(video=output_filename, caption="✅ **Download Successful!**")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ **Extraction Failed:** File size too small or cookie expired.")

    except Exception as err:
        logger.error(f"Execution Error: {str(err)}")
        await status_msg.edit_text(f"❌ **Critical Error:** `{str(err)[:120]}`")

    finally:
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except Exception:
                pass

if __name__ == "__main__":
    app.run()
