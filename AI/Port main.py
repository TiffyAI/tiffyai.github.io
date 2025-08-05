import os
import asyncio
import logging
import requests
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("RENDER_EXTERNAL_URL")  # Provided by Render
CERT_PATH = None  # if needed

PRICE_API_URL = "https://tiffyai.github.io/TIFFY-Market-Value/price.json"
PORTAL_LINK = "https://t.me/TiffyAI_Bot?start=portal"
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
TOKEN_CONTRACT = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔵 Welcome to TiffyAI... Use /claim to begin.", parse_mode="Markdown")

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = " ".join(context.args)
    if not user_input:
        await update.message.reply_text("🤖 Ask something after /ai", parse_mode="Markdown")
        return
    try:
        resp = requests.post(
            os.getenv("AI_BACKEND_URL"),
            json={"messages":[{"role":"system","content":"You're TiffyAI, crypto oracle."}, {"role":"user","content":user_input}]},
            timeout=15
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(content)
    except Exception as e:
        await update.message.reply_text("⚠️ AI error.")
        logging.error("AI backend failed: %s", e)

async def telegram_handler(request):
    body = await request.json()
    update = Update.de_json(body, bot)
    await app.update_queue.put(update)
    return PlainTextResponse("OK")

async def health(request):
    return PlainTextResponse("Alive")

async def run():
    global app, bot
    app = Application.builder().token(TOKEN).updater(None).build()
    bot = app.bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ai", ai))
    await app.initialize()
    await app.bot.set_webhook(url=f"{URL}/telegram")
    await app.start()
    return app

star = Starlette(
    routes=[
        Route("/telegram", telegram_handler, methods=["POST"]),
        Route("/healthcheck", health),
    ],
)

async def main():
    application = await run()
    config = uvicorn.Config(star, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
