import os
import logging
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_BACKEND_URL = os.getenv("AI_BACKEND_URL")  # e.g. https://tiffyai-bot.onrender.com/ask
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
PRICE_API_URL = "https://tiffyai.github.io/TIFFY‑Market‑Value/price.json"
TOKEN_CONTRACT = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"

app = Application.builder().token(BOT_TOKEN).build()

# --- Telegram Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔵 Welcome to *TiffyAI*! Tap /claim for your Blue Key journey.",
        parse_mode="Markdown"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(PRICE_API_URL)
        value = float(r.json().get("tiffyToUSD", 0))
        await update.message.reply_text(f"💎 $TIFFY: *${value:.4f}*", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Price fetch error.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(f"https://api.bscscan.com/api?module=token&action=tokenholderlist&contractaddress={TOKEN_CONTRACT}&page=1&offset=5&apikey={BSCSCAN_API_KEY}")
        holders = r.json().get("result", [])
        msg = "🏆 Top Holders:\n"
        for h in holders[:5]:
            bal = int(h["TokenHolderQuantity"]) / 1e18
            addr = h["TokenHolderAddress"]
            msg += f"`{addr[:6]}...{addr[-4:]}` — {bal:.2f} $TIFFY\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Leaderboard unavailable.")

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = " ".join(context.args)
    if not user_input:
        await update.message.reply_text("🤖 Use `/ai [your question]`, e.g. `/ai How to stake TIFFY?`")
        return
    logging.info("➡️ AI request: %s", user_input)
    try:
        r = requests.post(AI_BACKEND_URL, timeout=20, json={
            "messages":[{"role":"system","content":"You are TiffyAI, the ultimate Web3 oracle."},
                        {"role":"user","content":user_input}]
        })
        r.raise_for_status()
        resp = r.json()
        message = resp["choices"][0]["message"]["content"]
        await update.message.reply_text(message)
    except Exception as e:
        logging.error("AI error: %s", e)
        await update.message.reply_text("⚠️ AI backend error.")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("ai", ai))

web = FastAPI()

@web.on_event("startup")
async def bot_startup():
    await app.initialize()
    await app.start()
    # Remove any legacy webhook
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(f"{RENDER_URL}/telegram")
    logging.info("Webhook set to %s/telegram", RENDER_URL)

@web.on_event("shutdown")
async def bot_shutdown():
    await app.stop()
    await app.shutdown()

@web.post("/telegram")
async def telegram_webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, app.bot)
    await app.update_queue.put(update)
    return {"status":"ok"}

@web.get("/healthcheck")
async def health():
    return {"status":"alive"}

@web.get("/")
async def root():
    return {"status":"TiffyAI Bot & Web Service Online"}

if __name__ == "__main__":
    uvicorn.run(web, host="0.0.0.0", port=8000)
