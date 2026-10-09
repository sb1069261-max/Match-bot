import os
import threading
import telebot
from flask import Flask, redirect, render_template_string, request, session, url_for

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TOKEN:
    TOKEN = TOKEN.strip()

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
app.secret_key = os.urandom(24)

SECRET_PASSWORD = "/14VI40"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIP Bet - Dostęp</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 100%; max-width: 350px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #334155; background: #0f172a; color: #fff; border-radius: 6px; box-sizing: border-box; }
        button { background: #2563eb; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background: #1d4ed8; }
        .error { color: #f87171; font-size: 14px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        {% if not logged_in %}
            <h2>Podaj tajne hasło</h2>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <input type="password" name="password" placeholder="Hasło dostępu" required>
                <button type="submit">Wejdź do aplikacji</button>
            </form>
        {% else %}
            <h2>Witaj w VIP Bet!</h2>
            <p>Masz pełny dostęp do analiz i kursów na żywo.</p>
        {% endif %}
    </div>
</body>
</html>
"""


@bot.message_handler(commands=["14VI40"])
def handle_command(message):
    sent_message = bot.reply_to(
        message,
        "Witaj! Kliknij poniższy link, aby otworzyć aplikację: "
        "https://match-bot-nal2.onrender.com",
    )
    try:
        # Automatyczne przypięcie wiadomości z linkiem na górze grupy
        bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    except Exception as e:
        print(f"Nie udało się przypiąć wiadomości (bot może nie mieć uprawnień administratora): {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == SECRET_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        else:
            error = "Niepoprawne hasło!"

    logged_in = session.get("authenticated", False)
    return render_template_string(
        HTML_TEMPLATE, logged_in=logged_in, error=error
    )


def run_bot():
    bot.infinity_polling()


if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
