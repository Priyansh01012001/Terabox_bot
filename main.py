import os
import threading
import wget
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Terabox Bot is running with API!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
TBX_API_KEY = os.environ.get("API_KEY", "")
TBX_API_SECRET = os.environ.get("API_SECRET", "")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! TeraBox link bhejo.")

def get_video_from_api(terabox_url):
    api_endpoint = "https://api.apify.com/v2/acts/scraper-mind~terabox-downloader/run-sync-get-dataset-items"
    
    headers = {
        "Authorization": f"Bearer {TBX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": terabox_url,
        "secret": TBX_API_SECRET
    }
    
    try:
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=60)
        print(f"API Status Code: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                return data[0].get("downloadLink") or data[0].get("url")
    except Exception as e:
        print(f"API Error: {e}")
        
    return None

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text.strip()
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("🔍 API ke through link process ho raha hai...")
        
        try:
            direct_link = get_video_from_api(text)
            
            if direct_link:
                await msg.edit_text("📤 Video mil gayi, download karke bhej rahe hain...")
                video_path = wget.download(direct_link, out="video.mp4")
                
                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    await message.reply_video(video=video_path, caption="✅ Yeh lo tumhari video!")
                    os.remove(video_path)
                    await msg.delete()
                    return

            # Clean URL to prevent button error
            clean_url = text.split()[0] if text else "https://terabox.com"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Open Link Directly", url=clean_url)]
            ])
            await msg.edit_text("⚠️ Direct video fetch nahi ho paya. Neeche diye button se khol lo:", reply_markup=keyboard)
            
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya valid TeraBox link bhejiye.")

print("Starting bot...")
app.run()
