import os
import glob
import threading
import asyncio
import wget
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from playwright.async_api import async_playwright

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Playwright Terabox Bot is running!"

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

def find_chromium_path():
    # Render ke path par jaakar khud chromium ka executable dhund lega chahe version koi bhi ho
    patterns = [
        "/opt/render/.cache/ms-playwright/chromium-*/chrome-linux64/chrome",
        "/opt/render/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
        "/root/.cache/ms-playwright/chromium-*/chrome-linux64/chrome"
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None

async def get_direct_video_link(url, ndus_cookie):
    async with async_playwright() as p:
        executable_path = find_chromium_path()
        
        launch_options = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        }
        
        if executable_path and os.path.exists(executable_path):
            launch_options["executable_path"] = executable_path

        try:
            browser = await p.chromium.launch(**launch_options)
        except Exception as e:
            print(f"Browser Launch Failed: {e}")
            return None

        context = await browser.new_context()
        
        if ndus_cookie:
            await context.add_cookies([{
                "name": "ndus",
                "value": ndus_cookie,
                "domain": ".terabox.com",
                "path": "/"
            }])
        
        page = await context.new_page()
        download_url = None
        
        try:
            def handle_request(req):
                nonlocal download_url
                if ".mp4" in req.url or "d.terabox.com/file" in req.url:
                    download_url = req.url

            page.on("request", handle_request)
            await page.goto(url, timeout=60000)
            await asyncio.sleep(7)
        except Exception as e:
            print(f"Playwright Error: {e}")
            
        await browser.close()
        return download_url

@app.on_message(filters.text & ~filters.command("start"))
async def handle_terabox(client, message):
    text = message.text
    if any(domain in text.lower() for domain in ["terabox", "terashare", "1024tera", "tera"]):
        msg = await message.reply_text("🔍 Browser se video extract ki ja rahi hai...")
        
        try:
            direct_link = await get_direct_video_link(text, TERABOX_NDUS)
            
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
