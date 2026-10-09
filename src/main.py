import os
from flask import Flask, request
import telebot
from telebot import types

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://t.me/pro_bot_analyzer_bot/app")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=["14VI40"])
def handle_auth(message):
  markup = types.InlineKeyboardMarkup()
  btn = types.InlineKeyboardButton(
      "🔥 Otwórz Terminal VIP LIVE", web_app=types.WebAppInfo(url=MINI_APP_URL)
  )
  markup.add(btn)
  bot.reply_to(
      message,
      "Masz już aktywny dostęp. Kliknij poniżej:",
      reply_markup=markup,
  )


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  json_string = request.get_data().decode("utf-8")
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return "!", 200


@app.route("/")
def index():
  return "Bot is running!", 200


if __name__ == "__main__":
  bot.remove_webhook()
  bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
