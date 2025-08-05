import os
import logging
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, Context

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_BACKEND_URL = os.getenv("AI_BACKEND_URL")  # must point to https://tiffyai-bot.onrender.com/ask
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
PRICE_API_URL = "https://tiffyai.github.io/TIFFY-Market-Value/price.json"
TOKEN_CONTRACT = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"
PORTAL_LINK = "https://t.me/TiffyAI_Bot?start=portal"

app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔵 Welcome to *TiffyAI*.\nYour Blue Key awaits. Use /claim to get started.",
        parse_mode="Markdown"
    )

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💼 MetaMask, Trust, OKX supported.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = requests.get(PRICE_API_URL)
        price = resp.json().get("tiffyToUSD", 0)
        await update.message.reply_text(f"💎 $TIFFY is currently: *${price:.4f}*", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Price fetch error.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.bscscan.com/api?module=token&action=tokenholderlist&contractaddress={TOKEN_CONTRACT}&page=1&offset=5&apikey={BSCSCAN_API_KEY}"
    try:
        resp = requests.get(url)
        holders = resp.json().get("result", [])
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
        return await update.message.reply_text("🤖 Try: /ai What is TIFFY?")
    logging.info("Mapping to AI: %s", user_input)
    try:
        resp = requests.post(AI_BACKEND_URL, timeout=20, json={
            "messages":[{"role":"system","content":"You are TiffyAI, oracle of blockchain."},
                        {"role":"user","content":user_input}]
        })
        resp.raise_for_status()
        cont = resp.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(cont)
    except Exception as err:
        logging.error("AI error: %s", err)
        await update.message.reply_text("⚠️ AI backend error.")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("wallet", wallet))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("ai", ai))

web = FastAPI()

@web.on_event("startup")
async def startup():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.bot.set_webhook(f"{RENDER_URL}/telegram")

@web.on_event("shutdown")
async def shutdown():
    await app.updater.stop()
    await app.stop()
    await app.shutdown()

@web.post("/telegram")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return {"status":"ok"}

@web.get("/healthcheck")
async def health():
    return {"status":"alive"}

@web.get("/")
async def root():
    return {"status":"TiffyAI Bot & web service is online"}

if __name__ == "__main__":
    uvicorn.run(web, host="0.0.0.0", port=8000)
