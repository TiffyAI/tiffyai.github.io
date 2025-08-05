import os, logging, asyncio, requests
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, FileResponse
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("RENDER_EXTERNAL_URL")
PORTAL_LINK = "https://t.me/TiffyAI_Bot?start=portal"
PRICE_API_URL = "https://tiffyai.github.io/TIFFY-Market-Value/price.json"
CONTRACT = os.getenv("TOKEN_CONTRACT")

async def start(update: Update, ctx):
    await update.message.reply_text(f"🔵 Blue Key starts here ➤ {PORTAL_LINK}", parse_mode="Markdown")

async def telegram_webhook(request):
    body = await request.json()
    update = Update.de_json(body, bot)
    await app.update_queue.put(update)
    return PlainTextResponse("OK")

async def health(request):
    return PlainTextResponse("OK")

async def website(request):
    return FileResponse('index.html')  # Make sure index.html lives in this service folder

star = Starlette(routes=[
    Route("/", website),
    Route("/telegram", telegram_webhook, methods=["POST"]),
    Route("/healthcheck", health),
])

async def run_bot():
    global app, bot
    app = Application.builder().token(TOKEN).updater(None).build()
    bot = app.bot
    app.add_handler(CommandHandler("start", start))
    # Add your other handlers here...
    await app.initialize()
    await app.bot.set_webhook(url=f"{APP_URL}/telegram")
    await app.start()
    return app

if __name__ == "__main__":
    import uvicorn
    asyncio.run(run_bot())
    uvicorn.run(star, host="0.0.0.0", port=8000)
