import os
import asyncio
from flask import Flask, request

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")  # https://english-quiz-bot-mrsm.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")
PORT = int(os.getenv("PORT", "10000"))

flask_app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я живой. Скоро подключим вопросы.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ок: " + (update.message.text or ""))

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@flask_app.get("/")
def health():
    return "ok", 200

@flask_app.post(f"/webhook/{WEBHOOK_SECRET}")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    async def _process():
        async with application:
            await application.initialize()
            await application.process_update(update)

    asyncio.run(_process())
    return "ok", 200

if __name__ == "__main__":
    # ставим webhook (HTTPS URL обязателен)
    if PUBLIC_URL:
        asyncio.run(application.bot.set_webhook(f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"))
    flask_app.run(host="0.0.0.0", port=PORT)
