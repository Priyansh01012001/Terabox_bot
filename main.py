import os
import threading
import yt_dlp
from flask import Flask
from pyrogram import Client, filters

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Terabox Video Bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

# Yahan apni wahi ndus cookie ki value daal de jo screen par hai
NDUS_COOKIE = "YVOf2LVPeHuiSROI62W-_icpi1Ifdv-FV_QuBXQ"

app = Client("terabox_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! TeraBox link bhejo.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text.strip()
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("📥 Video download ho rahi hai...")
        
        clean_url = text.split()[0]
        output_filename = "video.mp4"
        
        # yt-dlp options with direct cookie header
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_filename,
            'http_headers': {
                'Cookie': f'ndus={NDUS_COOKIE}'
            },
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clean_url])
                
            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                await message.reply_video(
                    video=output_filename,
                    caption="✅ Yeh lo tumhari video!"
                )
                os.remove(output_filename)
                await msg.delete()
            else:
                await msg.edit_text("❌ Video download nahi ho payi.")
                
        except Exception as e:
            if os.path.exists(output_filename):
                os.remove(output_filename)
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya valid TeraBox link bhejiye.")

print("Starting bot...")
app.run()
