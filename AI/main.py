import os
import logging
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")

PRICE_API_URL = "https://tiffyai.github.io/TIFFY-Market-Value/price.json"
TOKEN_CONTRACT = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"
PORTAL_LINK = "https://tiffyai.github.io/Start"
STAR_AI_LINK = "https://t.me/TheStarAIBot/StarAI?startapp=aW52aXRhdGlvbl9jb2RlPUsxOXc3dyZwYWdlTmFtZT1hZ2VudHMmSWQ9YWUwNzMzNjQtZTIzZi00ZjQ5LTgzZmItYzM0YjdkMDAxMGJh"

# --- Telegram Bot ---
app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔵 Welcome to *TiffyAI*! Tap /claim to unlock your Blue Key portal.",
        parse_mode="Markdown"
    )

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🚪 Enter the TiffyAI Portal ➤ {PORTAL_LINK}",
        parse_mode="Markdown"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(PRICE_API_URL, timeout=5)
        price = float(r.json().get("tiffyToUSD", 0))
        await update.message.reply_text(
            f"💎 Current $TIFFY price: *${price:.4f}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error("Price fetch error: %s", e)
        await update.message.reply_text("⚠️ Sorry, price unavailable.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(
            f"https://api.bscscan.com/api?module=token&action=tokenholderlist"
            f"&contractaddress={TOKEN_CONTRACT}&page=1&offset=5&apikey={BSCSCAN_API_KEY}",
            timeout=5
        )
        holders = r.json().get("result", [])
        msg = "🏆 Top $TIFFY Holders:\n"
        for h in holders[:5]:
            bal = int(h["TokenHolderQuantity"]) / 1e18
            addr = h["TokenHolderAddress"]
            msg += f"`{addr[:6]}...{addr[-4:]}` — {bal:.2f} $TIFFY\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logging.error("Leaderboard fetch error: %s", e)
        await update.message.reply_text("⚠️ Leaderboard unavailable.")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Wallets Supported:*\n\n"
        "- OKX\n"
        "- Trust Wallet\n"
        "- MetaMask\n\n"
        "Connect through ➤ https://tiffyai.github.io/Start",
        parse_mode="Markdown"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *About $TIFFY Token:*\n\n"
        "TIFFY powers the TiffyAI ecosystem.\n"
        "- Earn it via quests & faucets\n"
        "- Stake & trade it in the future\n\n"
        "Explore ➤ https://www.tiffyai.co.za",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ *Bot Help Guide:*\n\n"
        "`/start` – Intro\n"
        "`/claim` – Portal link\n"
        "`/wallet` – Wallet options\n"
        "`/price` – Check token value\n"
        "`/leaderboard` – Top holders\n"
        "`/info` – Token overview\n"
        "`/ai` – Use Star AI\n"
        "`/help` – This guide",
        parse_mode="Markdown"
    )

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌟 Chat with Tiffy AI ➤ [Launch Star AI]({STAR_AI_LINK})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# --- Register Commands ---
commands = [
    ("start", start),
    ("claim", claim),
    ("price", price),
    ("leaderboard", leaderboard),
    ("wallet", wallet),
    ("info", info),
    ("help", help_command),
    ("ai", ai),
]

for cmd, func in commands:
    app.add_handler(CommandHandler(cmd, func))

# --- FastAPI Web Server ---
web = FastAPI()

@web.on_event("startup")
async def startup():
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(f"{RENDER_URL}/telegram")
    webhook_info = await app.bot.get_webhook_info()
    logging.info("✅ Webhook set to: %s", webhook_info.url)

@web.on_event("shutdown")
async def shutdown():
    await app.stop()
    await app.shutdown()

@web.post("/telegram")
async def incoming(request: Request):
    body = await request.json()
    logging.info("📩 Telegram update: %s", body)
    update = Update.de_json(body, app.bot)
    await app.process_update(update)
    return {"status": "ok"}

@web.get("/")
async def root():
    return {"message": "TiffyAI Bot Running Clean 🧼"}

@web.get("/healthcheck")
async def health():
    return {"status": "alive"}

if __name__ == "__main__":
    uvicorn.run("main:web", host="0.0.0.0", port=8000)
