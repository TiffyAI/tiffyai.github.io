import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")

TOKEN_CONTRACT = "0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5"
PRICE_API_URL = "https://tiffyai.github.io/TIFFY-Market-Value/price.json"
PORTAL_LINK = "https://tiffyai.github.io/Start/"
AI_BACKEND_URL = "https://tiffyai-bot.onrender.com/ask"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔵 Welcome to *TiffyAI*.\n\nYour Blue Key awaits.\n\n🎯 Every 10 minutes is a chance to claim, win, or unlock something powerful.\n\nUse /claim to begin.",
        parse_mode="Markdown"
    )

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🚪 Tap to enter the portal:\n{PORTAL_LINK}")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💼 Choose your wallet:\n\n🔗 MetaMask: Paste link in Discover\n🔗 TrustWallet: Open with DApp browser\n🔗 OKX: Use DApp scanner"
    )

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Token Stats & Trade Info:\n\n📍 Contract: `0xE488253DD6B4D31431142F1b7601C96f24Fb7dd5`\n\n📈 Trade: https://pancakeswap.finance/swap\n\n🔁 Slippage: ~2-5%\n\nUse /price to check current value.",
        parse_mode="Markdown"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(PRICE_API_URL)
        data = r.json()
        price = float(data.get("tiffyToUSD", 0))
        await update.message.reply_text(f"💎 Current $TIFFY: *${price:.4f}*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⚠️ Couldn't fetch price.")
        logger.error("Price fetch error: %s", e)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (
        f"https://api.bscscan.com/api?module=token&action=tokenholderlist"
        f"&contractaddress={TOKEN_CONTRACT}&page=1&offset=5&apikey={BSCSCAN_API_KEY}"
    )
    try:
        r = requests.get(url)
        holders = r.json().get("result", [])
        if not holders:
            raise Exception("Empty result")
        msg = "🏆 *Top $TIFFY Holders:*\n\n"
        for h in holders:
            addr = h["TokenHolderAddress"]
            bal = int(h["TokenHolderQuantity"]) / 10**18
            msg += f"`{addr[:6]}...{addr[-4:]}` — {bal:.2f} $TIFFY\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⚠️ Leaderboard unavailable.")
        logger.error("Leaderboard error: %s", e)

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = " ".join(context.args)
    if not user_input:
        await update.message.reply_text("🤖 Ask something after `/ai`, e.g. `/ai What is TiffyAI?`", parse_mode="Markdown")
        return
    try:
        response = requests.post(
            AI_BACKEND_URL,
            json={
                "messages": [
                    {"role": "system", "content": "You are TiffyAI, an ultra-intelligent Web3 oracle and crypto assistant."},
                    {"role": "user", "content": user_input}
                ]
            },
            timeout=15
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ AI backend error.")
        logger.error("AI request failed: %s", e)

# --- Bot Bootstrap ---

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("trade", trade))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("ai", ai))

    logging.info("🤖 TiffyAI Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
