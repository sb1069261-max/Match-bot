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
    <title>VIP Bet by Hrabia - Analytics & Predictions</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Login Screen */
        .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card-login { background: #1c2541; padding: 40px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); width: 100%; max-width: 380px; text-align: center; border: 1px solid #3a506b; }
        .card-login h2 { margin-bottom: 20px; color: #4cc9f0; }
        .card-login input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #3a506b; background: #0b132b; color: #fff; border-radius: 8px; font-size: 16px; }
        .card-login button { background: #4361ee; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
        .card-login button:hover { background: #3f37c9; }
        .error { color: #f72585; margin-bottom: 15px; font-size: 14px; }

        /* Main Dashboard */
        header { background: #1c2541; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3a506b; }
        .logo { font-size: 22px; font-weight: bold; color: #d4af37; letter-spacing: 1px; }
        .logo span { color: #ffffff; font-size: 14px; display: block; font-weight: normal; }
        nav button { background: #3a506b; color: white; border: none; padding: 8px 16px; border-radius: 20px; margin-left: 8px; cursor: pointer; font-size: 13px; }
        nav button.active { background: #4361ee; }

        .container { display: grid; grid-template-columns: 300px 1fr 320px; gap: 20px; padding: 20px; flex: 1; }
        @media (max-width: 1024px) { .container { grid-template-columns: 1fr; } }

        .panel { background: #1c2541; border-radius: 12px; padding: 18px; border: 1px solid #2a3a5e; }
        .panel-title { font-size: 15px; font-weight: 600; color: #4cc9f0; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px; }

        /* Left Side: Fixtures */
        .fixture-item { background: #0b132b; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid #2a3a5e; }
        .teams { display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
        .status-badge { font-size: 11px; background: rgba(76, 201, 240, 0.1); color: #4cc9f0; padding: 4px 8px; border-radius: 12px; text-align: center; }

        /* Center: Live Match Analytics */
        .live-score { display: flex; justify-content: space-around; align-items: center; background: #0b132b; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .team-name { font-size: 18px; font-weight: bold; width: 35%; text-align: center; }
        .score { font-size: 32px; font-weight: bold; color: #4cc9f0; }
        .match-time { color: #f72585; font-size: 12px; font-weight: bold; }

        .stat-bar { margin-bottom: 10px; }
        .stat-labels { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; color: #a0aec0; }
        .bar-bg { background: #0b132b; height: 8px; border-radius: 4px; overflow: hidden; display: flex; }
        .bar-fill { background: #4361ee; height: 100%; }

        /* Bot Verdict Panel */
        .verdict-box { background: rgba(67, 97, 238, 0.15); border: 1px solid #4361ee; border-radius: 10px; padding: 15px; margin-top: 15px; text-align: center; }
        .verdict-title { font-size: 13px; color: #a0aec0; }
        .verdict-value { font-size: 20px; font-weight: bold; color: #4cc9f0; margin: 5px 0; }
        .recommendation { background: #4cc9f0; color: #0b132b; font-weight: bold; padding: 8px; border-radius: 6px; margin-top: 10px; display: inline-block; width: 100%; }

        /* Right Side: Live Odds & Events */
        .odds-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }
        .odd-card { background: #0b132b; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #2a3a5e; }
        .odd-card.highlight { border-color: #4cc9f0; background: rgba(76, 201, 240, 0.1); }
        .odd-label { font-size: 11px; color: #a0aec0; }
        .odd-val { font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 4px; }

        .event-item { font-size: 12px; padding: 8px 0; border-bottom: 1px solid #2a3a5e; color: #a0aec0; display: flex; justify-content: space-between; }
        .event-time { color: #4cc9f0; font-weight: bold; }
    </style>
</head>
<body>

{% if not logged_in %}
    <div class="login-container">
        <div class="card-login">
            <h2>VIP BET BY HRABIA</h2>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <input type="password" name="password" placeholder="Podaj hasło dostępu" required>
                <button type="submit">Odblokuj Panel Analytics</button>
            </form>
        </div>
    </div>
{% else %}
    <header>
        <div class="logo">VIP bet <span>by hrabia</span></div>
        <nav>
            <button class="active">Pulpit</button>
            <button>Mecze Na Żywo</button>
            <button>Typy AI</button>
            <button>Statystyki</button>
            <button>Terminarz</button>
        </nav>
    </header>

    <div class="container">
        <!-- Lewa Kolumna: Nadchodzące Mecze -->
        <div class="panel">
            <div class="panel-title">Nadchodzące Mecze</div>
            
            <div class="fixture-item">
                <div class="teams"><span>LIVERPOOL</span> <span>CHELSEA</span></div>
                <div class="status-badge">Dzisiaj 20:00 • Analiza dostępna</div>
            </div>

            <div class="fixture-item">
                <div class="teams"><span>MAN CITY</span> <span>TOTTENHAM</span></div>
                <div class="status-badge">Dzisiaj 22:30 • Analiza dostępna</div>
            </div>

            <div class="fixture-item">
                <div class="teams"><span>BARCELONA</span> <span>REAL MADRYT</span></div>
                <div class="status-badge">Jutro 16:00 • Analiza przedmeczowa</div>
            </div>
        </div>

        <!-- Środkowa Kolumna: Analiza Meczowa Na Żywo -->
        <div class="panel">
            <div class="panel-title">Analiza Na Żywo - Premier League</div>
            
            <div class="live-score">
                <div class="team-name">MAN UTD</div>
                <div style="text-align: center;">
                    <div class="score">1 - 0</div>
                    <div class="match-time">28:34 LIVE</div>
                </div>
                <div class="team-name">ARSENAL</div>
            </div>

            <div class="stat-bar">
                <div class="stat-labels"><span>Posiadanie piłki: 55%</span><span>45%</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 55%;"></div></div>
            </div>

            <div class="stat-bar">
                <div class="stat-labels"><span>Strzały celne: 16</span><span>3</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 80%;"></div></div>
            </div>

            <div class="stat-bar">
                <div class="stat-labels"><span>Rzuty rożne: 4</span><span>7</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width: 36%;"></div></div>
            </div>

            <!-- Panel Rekomendacji Bota -->
            <div class="verdict-box">
                <div class="verdict-title">WERDYKT BOTA / PROGNOZA SI</div>
                <div class="verdict-value">Szansa wygranej gospodarzy: 68%</div>
                <div>Oczekiwane gole (xG): 2.1 - 1.1</div>
                <div class="recommendation">SUGEROWANY TYP: Wygrana Man Utd (1)</div>
            </div>
        </div>

        <!-- Prawa Kolumna: Kursy Live & Zdarzenia -->
        <div class="panel">
            <div class="panel-title">Kursy Na Żywo</div>
            <div class="odds-grid">
                <div class="odd-card highlight">
                    <div class="odd-label">1 (Gospodarze)</div>
                    <div class="odd-val">1.75</div>
                </div>
                <div class="odd-card">
                    <div class="odd-label">X (Remis)</div>
                    <div class="odd-val">3.50</div>
                </div>
                <div class="odd-card">
                    <div class="odd-label">2 (Goście)</div>
                    <div class="odd-val">5.00</div>
                </div>
            </div>

            <div class="panel-title">Ostatnie Zdarzenia</div>
            <div class="event-item">
                <span>Żółta kartka</span> <span class="event-time">79'</span>
            </div>
            <div class="event-item">
                <span>GOL! Man Utd (1-0)</span> <span class="event-time">35'</span>
            </div>
            <div class="event-item">
                <span>Żółta kartka</span> <span class="event-time">12'</span>
            </div>
        </div>
    </div>
{% endif %}

</body>
</html>
"""

@bot.message_handler(commands=["14VI40"])
def handle_command(message):
    sent_message = bot.reply_to(
        message,
        "Witaj! Kliknij poniższy link, aby otworzyć aplikację: "
        "https://match-bot-nal2.onrender.com"
    )
    try:
        bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    except Exception as e:
        print(f"Błąd przypinania: {e}")

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
    return render_template_string(HTML_TEMPLATE, logged_in=logged_in, error=error)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
