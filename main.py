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
            
            # API ke JSON response ke andar se download link nikalna
            direct_url = None
            try:
                if isinstance(data, dict):
                    inner_data = data.get("data", {})
                    if isinstance(inner_data, dict):
                        direct_url = (
                            inner_data.get("download_link") 
                            or inner_data.get("url") 
                            or inner_data.get("link") 
                            or inner_data.get("dlink")
                            or inner_data.get("download")
                        )
                    
                    if not direct_url:
                        direct_url = (
                            data.get("download_url") 
                            or data.get("link") 
                            or data.get("url") 
                            or data.get("download")
                        )
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
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Open TeraBox Link", url=text)]
                ])
                await msg.edit_text(
                    f"⚠️ Response mil gaya par link key alag hai. Full response:\n`{str(data)[:200]}`",
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
