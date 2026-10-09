import os
import threading
import telebot
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TOKEN:
    TOKEN = TOKEN.strip()

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=["14VI40"])
def handle_command(message):
    bot.reply_to(
        message,
        "Witaj! Kliknij poniższy link, aby otworzyć aplikację: "
        "https://match-bot-nal2.onrender.com",
    )


@app.route("/")
def index():
    return "Bot is running!"


def run_bot():
    # Uruchomienie nasłuchu wiadomości (polling) w tle
    bot.infinity_polling()


if __name__ == "__main__":
    # Uruchomienie wątku z botem Telegrama
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    # Uruchomienie serwera Flask dla Rendera
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
