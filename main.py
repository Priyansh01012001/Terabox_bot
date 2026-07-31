import os
import threading
from flask import Flask
from pyrogram import Client, filters

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
        await message.reply_text(f"Aapne Terabox link bheja hai: {text}\n(Yahan aap apna download logic laga sakte hain)")
    else:
        await message.reply_text("Kripya ek valid TeraBox link bhejiye.")

print("Bot is starting...")
app.run()
