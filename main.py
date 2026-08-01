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
        msg = await message.reply_text("📥 Link process ho raha hai...")
        
        clean_url = text.split()[0]
        output_filename = "video.mp4"
        
        try:
            session = requests.Session()
            # Load cookie if exists
            cookies = {}
            if os.path.exists('cookies.txt'):
                cookies['ndus'] = "YVOf2LVPeHuiSROI62W-_icpi1Ifdv-FV_QuBXQ"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.terabox.com/'
            }
            
            # Request sharing page
            resp = session.get(clean_url, headers=headers, cookies=cookies, allow_redirects=True, timeout=30)
            
            if resp.status_code == 200:
                # Basic extraction logic for direct stream
                # If direct page html contains dlink, grab it
                import re
                dlink_match = re.search(r'"dlink"\s*:\s*"([^"]+)"', resp.text)
                
                if dlink_match:
                    download_url = dlink_match.group(1).replace(r'\/', '/')
                    
                    await msg.edit_text("📥 Video download ho rahi hai...")
                    vid_data = session.get(download_url, headers=headers, cookies=cookies, stream=True, timeout=60)
                    
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
                    await msg.edit_text("❌ Cookies ya link expired hai, dlink nahi mila page par.")
            else:
                await msg.edit_text(f"❌ Terabox server error: Status code {resp.status_code}")
                
        except Exception as e:
            if os.path.exists(output_filename):
                os.remove(output_filename)
            await msg.edit_text(f"❌ Error: {str(e)}")
    else:
        await message.reply_text("Kripya valid TeraBox link bhejiye.")

print("Starting bot...")
app.run()
