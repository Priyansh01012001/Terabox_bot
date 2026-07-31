import os
import threading
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Flask dummy server taaki Render ka port wala error na aaye
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

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! Main TeraBox bot hoon. Mujhe TeraBox ka link bhejo, main direct link nikalne ki koshish karta hoon.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "terasharefile", "tera"]):
        msg = await message.reply_text("🔍 TeraBox link se direct video link extract kiya ja raha hai...")
        
        try:
            # Free public parser endpoint / wrapper
            api_url = f"https://terabox-dl.red-devils-api.workers.dev/?url={text}"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            
            # Agar direct link mil gaya
            if "download_url" in data or "link" in data:
                direct_url = data.get("download_url") or data.get("link")
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Download Video Now", url=direct_url)]
                ])
                
                await msg.edit_text(
                    "✅ **Direct Video Link Found!**\n\nNiche diye gaye button par click karke seedha download karein:",
                    reply_markup=keyboard
                )
            else:
                # Agar API se direct link na mile toh normal link button bhej do
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Open TeraBox Link", url=text)]
                ])
                await msg.edit_text(
                    "⚠️ Direct link fetch nahi ho paya. Aap is button se open kar sakte hain:",
                    reply_markup=keyboard
                )
        except Exception as e:
            # Fallback agar API down ho
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Open Link", url=text)]
            ])
            await msg.edit_text(
                "✅ **TeraBox Link Processed!**\n\nButton par click karein:",
                reply_markup=keyboard
            )
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting...")
app.run()

