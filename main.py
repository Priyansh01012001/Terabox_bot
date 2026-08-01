import os
import threading
import subprocess
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
TERABOX_NDUS = os.environ.get("TERABOX_NDUS", "")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Hello! TeraBox Downloader Bot ready hai. Koi bhi TeraBox link bhejo!")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("🔍 Link process ho raha hai, thoda wait karo...")
        
        try:
            video_path = "video.mp4"
            if os.path.exists(video_path):
                os.remove(video_path)
            
            # Updated command with proper cookie headers to bypass restrictions
            command = f'yt-dlp --no-check-certificates --add-header "Cookie: ndus={TERABOX_NDUS}" -o {video_path} "{text}"'
            
            process = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                await msg.edit_text("📤 Video download ho gayi, Telegram par bhej rahe hain...")
                await message.reply_video(video=video_path, caption="✅ Yeh lo tumhari video!")
                
                if os.path.exists(video_path):
                    os.remove(video_path)
                await msg.delete()
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Open Link Directly", url=text)]
                ])
                await msg.edit_text("⚠️ Direct download fail ho gaya. Neeche diye button se khol lo:", reply_markup=keyboard)
        except Exception as e:
            await msg.edit_text(f"❌ Error aa gaya: {str(e)}")
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting up...")
app.run()
