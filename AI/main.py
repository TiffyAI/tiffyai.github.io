import os
import requests
import logging
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, PlainTextResponse, FileResponse
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_BACKEND_URL = os.getenv("AI_BACKEND_URL")  # e.g. https://tiffyai-cloud.onrender.com/ask
PORTAL_LINK = "https://t.me/TiffyAI_Bot?start=portal"
PRICE_API_URL = "https://tiffyai.github.io/TIFFY‑Market‑Value/price.json"
TOKEN_CONTRACT = os.getenv("TOKEN_CONTRACT")

# Telegram Handlers
async def start(update: Update, context):
    await update.message.reply_text("🔵 Welcome to TiffyAI… Use /claim", parse_mode="Markdown")

# Add AI, price, leaderboard similarly...

async def telegram_webhook(request):
    body = await request.json()
    update = Update.de_json(body, bot)
    await app.update_queue.put(update)
    return PlainTextResponse("OK")

# Health
async def health(request):
    return PlainTextResponse("OK")

# Serve your site (either static HTML or from GitHub hosted folder)
async def website(request):
    return FileResponse('AI/index.html')  # adjust path if needed

# Setup Starlette App
routes = [
    Route("/", website),
    Route("/healthcheck", health),
    Route("/telegram", telegram_webhook, methods=["POST"]),
]

star = Starlette(routes=routes)

async def run():
    global app, bot
    app = Application.builder().token(BOT_TOKEN).updater(None).build()
    bot = app.bot
    app.add_handler(CommandHandler("start", start))
    # add other handlers
    await app.initialize()
    await app.bot.set_webhook(url=f"{os.getenv('RENDER_EXTERNAL_URL')}/telegram")
    await app.start()
    return app

if __name__ == "__main__":
    import uvicorn
    import asyncio
    asyncio.run(run())
    uvicorn.run(star, host="0.0.0.0", port=8000)
