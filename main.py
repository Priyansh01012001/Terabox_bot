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
RAPIDAPI_HOST = "terabox-downloader-online-viewer-player-api.p.rapidapi.com"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! Main TeraBox bot hoon. Mujhe TeraBox ka link bhejo, main direct link nikal kar deta hoon.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "terasharefile", "tera"]):
        msg = await message.reply_text("🔍 TeraBox link se direct video link extract kiya ja raha hai...")
        
        try:
            url = "https://terabox-downloader-online-viewer-player-api.p.rapidapi.com/rapidapi"
            
            querystring = {"url": text}
            headers = {
                "Content-Type": "application/json",
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": RAPIDAPI_KEY
            }

            response = requests.get(url, headers=headers, params=querystring, timeout=20)
            data = response.json()
            
            # JSON ke har possible jagah se link dhoondhna
            direct_url = None
            try:
                # Agar 'data' dictionary hai
                if isinstance(data, dict):
                    # 1. Direct keys check karo
                    direct_url = data.get("download_link") or data.get("link") or data.get("url") or data.get("download") or data.get("dlink")
                    
                    # 2. 'data' sub-object check karo
                    if not direct_url and isinstance(data.get("data"), dict):
                        sub = data.get("data")
                        direct_url = sub.get("download_link") or sub.get("link") or sub.get("url") or sub.get("download") or sub.get("dlink")
                        
                        # 3. 'structure' sub-object check karo
                        if not direct_url and isinstance(sub.get("structure"), dict):
                            st = sub.get("structure")
                            direct_url = st.get("download_link") or st.get("link") or st.get("url") or st.get("download") or st.get("dlink") or st.get("down_url") or st.get("direct_link")
            except:
                pass
            
            if direct_url:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Download Video Now", url=direct_url)]
                ])
                await msg.edit_text(
                    "✅ **Direct Video Link Found!**\n\nNiche diye gaye button par click karke seedha download karein:",
                    reply_markup=keyboard
                )
            else:
                # Agar phir bhi link nahi mila toh poora response print karwa lo taaki key pata chal jaye
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Open TeraBox Link", url=text)]
                ])
                await msg.edit_text(
                    f"⚠️ Full JSON Response:\n`{str(data)[:350]}`",
                    reply_markup=keyboard
                )
        except Exception as e:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Open Link", url=text)]
            ])
            await msg.edit_text(f"❌ Error: {str(e)}", reply_markup=keyboard)
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting...")
app.run()
