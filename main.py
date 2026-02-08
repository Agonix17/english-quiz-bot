import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")
PORT = int(os.getenv("PORT", "10000"))

flask_app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я живой. Скоро подключим вопросы.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ок: " + (update.message.text or ""))

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@flask_app.get("/")
def health():
    return "ok", 200

@flask_app.post(f"/webhook/{WEBHOOK_SECRET}")
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put(update)
    return "ok", 200

@flask_app.before_first_request
def set_webhook():
    if PUBLIC_URL:
        tg_app.bot.set_webhook(f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}")

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT)
