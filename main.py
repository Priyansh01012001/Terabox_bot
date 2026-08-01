import os
import threading
import wget
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Terabox Bot is running!"

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
    await message.reply_text("👋 Bot ready hai! TeraBox link bhejo.")

def get_video_with_ytdlp(url, ndus_cookie):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if ndus_cookie:
        headers['Cookie'] = f'ndus={ndus_cookie}'
        
    ydl_opts['http_headers'] = headers

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info['url']
            elif 'formats' in info:
                for f in info['formats']:
                    if f.get('url'):
                        return f['url']
    except Exception as e:
        print(f"YTDLP Error: {e}")
        return None
    return None

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("🔍 Link se video extract ki ja rahi hai...")
        
        try:
            direct_link = get_video_with_ytdlp(text, TERABOX_NDUS)
            
            if direct_link:
                await msg.edit_text("📤 Video mil gayi, download karke bhej rahe hain...")
                video_path = wget.download(direct_link, out="video.mp4")
                
                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    await message.reply_video(video=video_path, caption="✅ Yeh lo tumhari video!")
                    os.remove(video_path)
                    await msg.delete()
                    return

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Open Link Directly", url=text)]
            ])
            await msg.edit_text("⚠️ Direct stream extract nahi ho paya. Neeche diye button se khol lo:", reply_markup=keyboard)
            
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya valid TeraBox link bhejiye.")

print("Starting bot...")
app.run()
