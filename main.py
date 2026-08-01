import os
import threading
import requests
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

app = Client("terabox_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 Bot ready hai! TeraBox link bhejo.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text.strip()
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("📥 Link fetch ho raha hai...")
        
        clean_url = text.split()[0]
        output_filename = "video.mp4"
        
        try:
            # Using a public Terabox direct link fetching API approach
            api_endpoint = f"https://terabox-dl-api.details-apis.workers.dev/?url={clean_url}"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(api_endpoint, headers=headers, timeout=30)
            data = response.json()
            
            download_url = data.get("download_url") or data.get("url") or data.get("link")
            
            if not download_url:
                # Fallback API try
                api_endpoint_2 = f"https://teraboxwith-api.deta.dev/get?url={clean_url}"
                res2 = requests.get(api_endpoint_2, headers=headers, timeout=30)
                download_url = res2.json().get("download_url")

            if download_url:
                await msg.edit_text("📥 Video download ho rahi hai...")
                vid_data = requests.get(download_url, stream=True, timeout=60)
                
                with open(output_filename, 'wb') as f:
                    for chunk in vid_data.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                
                if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                    await message.reply_video(
                        video=output_filename,
                        caption="✅ Yeh lo tumhari video!"
                    )
                    os.remove(output_filename)
                    await msg.delete()
                else:
                    await msg.edit_text("❌ File download nahi ho payi.")
            else:
                await msg.edit_text("❌ Direct link extract nahi ho paya. Link expired ya invalid hai.")
                
        except Exception as e:
            if os.path.exists(output_filename):
                os.remove(output_filename)
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya valid TeraBox link bhejiye.")

print("Starting bot...")
app.run()
