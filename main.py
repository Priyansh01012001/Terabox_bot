import os
import threading
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

RAPIDAPI_KEY = "f52c8a1e41mshf5f5759d6b6e08bp1152efjsna891dad886b0"
RAPIDAPI_HOST = "terabox-downloader-and-player-api.p.rapidapi.com"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! Main TeraBox video bot hoon. Mujhe TeraBox link bhejo, main video download karke bhej dunga.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "terasharefile", "tera"]):
        msg = await message.reply_text("🔍 TeraBox link process ho raha hai...")
        
        try:
            url = "https://terabox-downloader-and-player-api.p.rapidapi.com/get"
            querystring = {"url": text}
            headers = {
                "Content-Type": "application/json",
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": RAPIDAPI_KEY
            }

            # Yeh GET request hai query parameters ke sath
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            data = response.json()
            
            # Direct video download link nikalna
            direct_url = None
            if isinstance(data, dict):
                direct_url = data.get("download_link") or data.get("link") or data.get("url") or data.get("download") or data.get("dlink")
                if not direct_url and isinstance(data.get("data"), dict):
                    sub = data.get("data")
                    direct_url = sub.get("download_link") or sub.get("link") or sub.get("url") or sub.get("download") or sub.get("dlink")
            
            if direct_url:
                await msg.edit_text("📥 Video download ho rahi hai, thoda wait karo...")
                
                # Video file ko chunk mein download karna
                video_res = requests.get(direct_url, stream=True, timeout=120)
                video_path = "downloaded_video.mp4"
                
                with open(video_path, "wb") as f:
                    for chunk in video_res.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                
                await msg.edit_text("📤 Telegram par video upload ki ja rahi hai...")
                
                # Telegram par video file bhej dena
                await message.reply_video(video=video_path, caption="✅ Yeh lo tumhari video!")
                
                # File delete karna server clean rakhne ke liye
                if os.path.exists(video_path):
                    os.remove(video_path)
                    
                await msg.delete()
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Open TeraBox Link", url=text)]
                ])
                await msg.edit_text(f"⚠️ API response:\n`{str(data)[:200]}`", reply_markup=keyboard)
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting...")
app.run()
