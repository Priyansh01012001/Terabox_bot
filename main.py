import os
import threading
import logging
import asyncio
import requests
import yt_dlp
from flask import Flask
from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxUltimateBot")

app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Ultimate Terabox Bot is active!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web_server, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "terabox_ultimate_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("🚀 **Ultimate Terabox Bot Online!** Link bhejo.")

@app.on_message(filters.text & ~filters.command("start"))
async def process_terabox_link(client, message):
    url_text = message.text.strip()
    
    if not any(domain in url_text.lower() for domain in ["terabox", "terashare", "1024tera", "tera", "nephobox"]):
        await message.reply_text("⚠️ Kripya ek valid TeraBox sharing link bhejiye.")
        return

    status_msg = await message.reply_text("⚙️ **Extracting direct streaming link...**")
    raw_url = url_text.split()[0]
    output_filename = f"media_{message.id}.mp4"

    try:
        # Using a reliable third-party open terabox resolution endpoint designed for bots
        api_endpoint = f"https://terabox-dl.pages.dev/api?url={raw_url}"
        
        session = requests.Session()
        resp = session.get(api_endpoint, timeout=25)
        data = resp.json()
        
        download_url = data.get("downloadLink") or data.get("dlink") or data.get("url")
        
        if not download_url:
            # Fallback to yt-dlp if API fails
            raise Exception("API direct link empty, falling back to yt-dlp")

        await status_msg.edit_text("📥 **Downloading video stream at high speed...**")
        
        vid_resp = session.get(download_url, stream=True, timeout=120)
        with open(output_filename, 'wb') as f:
            for chunk in vid_resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 50000:
            await status_msg.edit_text("📤 **Uploading video to Telegram...**")
            await message.reply_video(video=output_filename, caption="✅ **Poori Video Download Successful!**")
            await status_msg.delete()
        else:
            raise Exception("Downloaded file is too small or invalid.")

    except Exception as err:
        logger.warning(f"API Method failed, trying direct yt-dlp override: {str(err)}")
        try:
            ydl_options = {
                'format': 'best',
                'outtmpl': output_filename,
                'quiet': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                }
            }
            loop = asyncio.get_running_loop()
            def dl_fallback():
                with yt_dlp.YoutubeDL(ydl_options) as ydl:
                    ydl.download([raw_url])
            await loop.run_in_executor(None, dl_fallback)

            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 50000:
                await message.reply_video(video=output_filename, caption="✅ **Download Successful (Fallback Engine)!**")
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ **Failed:** TeraBox block kar raha hai. Link private ya protected hai.")
        except Exception as e2:
            await status_msg.edit_text(f"❌ **Error:** `{str(e2)[:100]}`")

    finally:
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except Exception:
                pass

if __name__ == "__main__":
    app.run()
