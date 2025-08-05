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
        "🔐 *Wallet Connection Guide:*\n\n"
        "You can connect your wallet using OKX, Trust Wallet, or MetaMask.\n\n"
        "Visit the portal ➤ https://tiffyai.github.io/Start and follow the connect prompts.\n\n"
        "Need help? DM @TiffyAI_Support",
        parse_mode="Markdown"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *About $TIFFY Token:*\n\n"
        "TIFFY is the native token powering the TiffyAI ecosystem.\n"
        "- Earn it via quests & faucets\n"
        "- Stake it in future updates\n"
        "- Trade it on decentralized exchanges\n\n"
        "Explore ➤ https://www.tiffyai.co.za",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ *Bot Help Guide:*\n\n"
        "`/start` – Introduction to TiffyAI\n"
        "`/claim` – Access the Blue Key portal\n"
        "`/wallet` – How to connect your wallet\n"
        "`/price` – Check the current $TIFFY token price\n"
        "`/leaderboard` – View top holders\n"
        "`/info` – Learn about the $TIFFY ecosystem\n"
        "`/help` – Show this help message\n",
        parse_mode="Markdown"
    )

# --- Register Commands ---
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("claim", claim))
app.add_handler(CommandHandler("price", price))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("wallet", wallet))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("help", help_command))

# --- FastAPI Server ---
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

# --- Launch ---
if __name__ == "__main__":
    uvicorn.run("main:web", host="0.0.0.0", port=8000)
