import os
import threading
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

# Flask server ko background thread mein chala rahe hain
threading.Thread(target=run_web, daemon=True).start()

# Apni details yahan daalein
API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! Main Terabox bot hoon. Mujhe Terabox ka link bhejo.")
@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "terasharefile", "tera"]):
        msg = await message.reply_text("🔍 TeraBox link ko process kiya ja raha hai...")
        
        try:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Download / Watch Online", url=text)]
            ])
            
            await msg.edit_text(
                "✅ **TeraBox Link Processed Successfully!**\n\nNiche diye gaye button par click karke aap apni video dekh ya download kar sakte hain:",
                reply_markup=keyboard
            )
        except Exception as e:
            await msg.edit_text(f"❌ Kuch error aa gaya: {str(e)}")
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting...")
app.run()
