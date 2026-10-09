import os
import telebot
from flask import Flask

# Pobranie tokena z automatycznym usunięciem spacji i enterów
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


# Obsługa wiadomości tekstowych / innych komend w grupach i czatach prywatnych
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Tutaj działa reszta logiki z dzisiejszego dnia
    pass


@app.route("/")
def index():
    return "Bot is running!"


if __name__ == "__main__":
    # Uruchomienie bota w tle lub standardowe webhooki/polling w zależności od konfiguracji Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
