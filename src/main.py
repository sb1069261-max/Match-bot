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
    <title>VIP bet by hrabia</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #030712; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Ekran Logowania */
        .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; padding: 20px; background: #000000; }
        .card-login { 
            background: linear-gradient(180deg, #0d1b3e 0%, #081026 100%); 
            padding: 40px 30px; 
            border-radius: 24px; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.9); 
            width: 100%; 
            max-width: 380px; 
            text-align: center; 
            border: 1px solid rgba(255,255,255,0.08); 
        }
        
        .logo-img { width: 140px; height: auto; margin-bottom: 20px; }
        .card-login h2 { font-family: 'Georgia', serif; font-style: italic; font-size: 28px; font-weight: normal; color: #ffffff; margin-bottom: 8px; letter-spacing: 0.5px; }
        .card-login p { color: #94a3b8; font-size: 13px; margin-bottom: 30px; line-height: 1.4; }
        
        .input-group { position: relative; width: 100%; margin-bottom: 20px; }
        .card-login input { 
            width: 100%; 
            padding: 16px 20px; 
            border: 1px solid #1e293b; 
            background: #060c1a; 
            color: #fff; 
            border-radius: 12px; 
            font-size: 15px; 
            outline: none; 
            box-sizing: border-box;
        }
        .card-login input::placeholder { color: #64748b; }
        
        .card-login button { 
            background: #0284c7; 
            color: white; 
            border: none; 
            padding: 16px; 
            width: 100%; 
            border-radius: 12px; 
            font-weight: 700; 
            font-size: 16px; 
            cursor: pointer; 
            transition: 0.2s; 
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3);
        }
        .card-login button:hover { background: #0369a1; }
        .error { color: #f43f5e; margin-bottom: 15px; font-size: 14px; font-weight: 600; }

        /* Nagłówek i Nawigacja */
        header { background: #081026; padding: 15px 20px; border-bottom: 1px solid #1e293b; position: sticky; top: 0; z-index: 1000; }
        .header-content { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; }
        .logo { font-size: 20px; font-weight: 900; color: #fbbf24; text-transform: uppercase; letter-spacing: 1px; }
        .logo span { color: #94a3b8; font-size: 11px; display: block; font-weight: 400; }
        
        .nav-tabs { display: flex; gap: 8px; overflow-x: auto; margin-top: 12px; padding-bottom: 4px; scrollbar-width: none; max-width: 1200px; margin-left: auto; margin-right: auto; }
        .nav-tabs::-webkit-scrollbar { display: none; }
        .nav-btn { background: #1e293b; color: #94a3b8; border: none; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: 0.2s; }
        .nav-btn.active { background: #0284c7; color: white; }

        /* Główny Kontener */
        .container { padding: 20px; max-width: 900px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 20px; flex: 1; }
        .section-view { display: none; flex-direction: column; gap: 15px; }
        .section-view.active { display: flex; }

        /* Karty Meczów i AI */
        .ai-master-card { background: #081026; border-radius: 16px; border: 1px solid #1e293b; padding: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.4); position: relative; overflow: hidden; }
        .ai-master-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #38bdf8; }
        
        .card-top-info { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; margin-bottom: 15px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }
        .live-pulse { color: #f43f5e; font-weight: bold; display: flex; align-items: center; gap: 5px; }
        .live-pulse::before { content: ''; width: 8px; height: 8px; background: #f43f5e; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

        /* Układ Drużyn i Szans AI */
        .matchup-grid { display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center; margin: 15px 0; }
        @media(max-width: 600px) { .matchup-grid { grid-template-columns: 1fr; gap: 15px; text-align: center; } }

        .team-box { background: #030712; border: 2px solid #1e293b; border-radius: 12px; padding: 14px; text-align: center; transition: 0.3s; }
        .team-name { font-size: 15px; font-weight: 800; margin-bottom: 6px; }
        .team-probability { font-size: 11px; font-weight: 700; text-transform: uppercase; }

        .team-box.winner { border-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
        .team-box.winner .team-name { color: #4ade80; }
        .team-box.winner .team-probability { color: #22c55e; }

        .team-box.loser { border-color: #f43f5e; background: rgba(244, 63, 94, 0.08); }
        .team-box.loser .team-name { color: #fb7185; }
        .team-box.loser .team-probability { color: #f43f5e; }

        .central-score-box { text-align: center; padding: 0 10px; }
        .score-display { font-size: 26px; font-weight: 900; color: #ffffff; letter-spacing: 2px; }
        .match-minute { font-size: 12px; color: #38bdf8; font-weight: bold; margin-top: 4px; }

        /* Mój Typ / Kupon AI */
        .coupon-header { background: linear-gradient(135deg, #0d1b3e 0%, #081026 100%); border: 1px solid #1e293b; border-radius: 16px; padding: 20px; margin-bottom: 15px; text-align: center; }
        .coupon-title { font-size: 20px; font-weight: 900; color: #38bdf8; margin-bottom: 6px; text-transform: uppercase; }
        .coupon-subtitle { font-size: 13px; color: #94a3b8; }
        
        .pick-item { background: #081026; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .pick-info h4 { font-size: 15px; color: #fff; margin-bottom: 4px; }
        .pick-info p { font-size: 12px; color: #38bdf8; font-weight: bold; }
        .pick-badge { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 14px; }

        /* Transmisje */
        .stream-box { background: #081026; border-radius: 16px; border: 1px solid #1e293b; padding: 20px; }
        .stream-container { position: relative; width: 100%; padding-bottom: 56.25%; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid #334155; }
        .stream-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }
        .stream-servers { display: flex; gap: 10px; margin-top: 15px; overflow-x: auto; }
        .server-btn { background: #1e293b; color: white; border: 1px solid #334155; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; flex-shrink: 0; }
        .server-btn.active { border-color: #0284c7; background: #0284c7; }
    </style>
</head>
<body>

{% if not logged_in %}
    <div class="login-container">
        <div class="card-login">
            <!-- Herb z Lwami i Puharem -->
            <svg class="logo-img" viewBox="0 0 200 160" xmlns="http://www.w3.org/2000/svg">
                <path d="M100 20 L120 60 L80 60 Z" fill="#d4af37"/>
                <path d="M100 30 C120 30 135 45 135 65 C135 90 100 115 100 115 C100 115 65 90 65 65 C65 45 80 30 100 30 Z" fill="#800020" stroke="#d4af37" stroke-width="3"/>
                <!-- Puchar -->
                <path d="M90 45 L110 45 L108 70 C108 78 92 78 92 70 Z" fill="#f59e0b" stroke="#fff" stroke-width="1"/>
                <path d="M97 78 L103 78 L103 88 L97 88 Z" fill="#f59e0b"/>
                <path d="M90 88 L110 88 L110 93 L90 93 Z" fill="#f59e0b"/>
                <!-- Lwy (Lwy po lewej i prawej stronie) -->
                <path d="M45 55 C40 40 55 35 60 50 C65 60 55 75 45 85 C40 75 35 65 45 55 Z" fill="#d4af37"/>
                <path d="M155 55 C160 40 145 35 140 50 C135 60 145 75 155 85 C160 75 165 65 155 55 Z" fill="#d4af37"/>
                <!-- Korona -->
                <path d="M85 22 L100 10 L115 22 L108 28 L92 28 Z" fill="#f59e0b"/>
            </svg>

            <h2>VIP bet by hrabia</h2>
            <p>Najlepszy na świecie system analityczny i predykcyjny</p>
            
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            
            <form method="POST">
                <div class="input-group">
                    <input type="password" name="password" placeholder="Wprowadź hasło" required>
                </div>
                <button type="submit">Uruchom AI Intelligence</button>
            </form>
        </div>
    </div>
{% else %}
    <header>
        <div class="header-content">
            <div class="logo">VIP bet <span>by hrabia • World-Class AI Engine v5.0</span></div>
        </div>
        <div class="nav-tabs">
            <button class="nav-btn active" onclick="switchTab('predictions', this)">🧠 Głęboka Analiza AI</button>
            <button class="nav-btn" onclick="switchTab('mytips', this)" style="background: #0284c7; color: #ffffff;">🎯 Mój Typ / Kupon AI</button>
            <button class="nav-btn" onclick="switchTab('livescore', this)">⚡ Wyniki na Żywo</button>
            <button class="nav-btn" onclick="switchTab('streams', this)">📺 Oglądaj Transmisje</button>
            <button class="nav-btn" onclick="switchTab('schedule', this)">📅 Terminarz</button>
        </div>
    </header>

    <div class="container">
        
        <!-- ZAKŁADKA 1: GŁĘBOKA ANALIZA AI -->
        <div id="predictions" class="section-view active">
            <div class="ai-master-card">
                <div class="card-top-info">
                    <span style="font-weight:700; color:#cbd5e1;">PREMIER LEAGUE • HIT KOLEJKI</span>
                    <span class="live-pulse">74' NA ŻYWO</span>
                </div>
                
                <div class="matchup-grid">
                    <div class="team-box winner">
                        <div class="team-name">MANCHESTER UTD</div>
                        <div class="team-probability">Szansa AI: 78% (Zwycięzca)</div>
                    </div>

                    <div class="central-score-box">
                        <div class="score-display">2 - 1</div>
                        <div class="match-minute">74 minuta</div>
                    </div>

                    <div class="team-box loser">
                        <div class="team-name">ARSENAL</div>
                        <div class="team-probability">Szansa AI: 22% (Zagrożony)</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ZAKŁADKA 2: MÓJ TYP / KUPON AI -->
        <div id="mytips" class="section-view">
            <div class="coupon-header">
                <div class="coupon-title">🎯 Kupon AI by Hrabia (Eksperckie Typy)</div>
                <div class="coupon-subtitle">Najpewniejsze typy wygenerowane przez sieć neuronową.</div>
            </div>

            <div class="pick-item">
                <div class="pick-info">
                    <h4>Manchester Utd vs Arsenal</h4>
                    <p>Typ AI: Wygrana Manchester Utd (1)</p>
                </div>
                <div class="pick-badge">1.72</div>
            </div>

            <div class="pick-item">
                <div class="pick-info">
                    <h4>Barcelona vs Real Madryt</h4>
                    <p>Typ AI: Wygrana Barcelony (1)</p>
                </div>
                <div class="pick-badge">1.95</div>
            </div>
        </div>

        <!-- ZAKŁADKA 3: WYNIKI NA ŻYWO -->
        <div id="livescore" class="section-view">
            <div class="stream-box">
                <iframe src="https://www.livescore.com/en/widget/football/" style="width:100%; height:600px; border:none;" scrolling="yes"></iframe>
            </div>
        </div>

        <!-- ZAKŁADKA 4: TRANSMISJE LIVE -->
        <div id="streams" class="section-box stream-box">
            <div class="stream-container">
                <iframe id="videoPlayer" src="https://strumyk.lol" allowfullscreen></iframe>
            </div>
            <div class="stream-servers">
                <button class="server-btn active" onclick="changeStream('https://strumyk.lol', this)">Strumyk</button>
                <button class="server-btn" onclick="changeStream('https://strims.in', this)">Strims</button>
            </div>
        </div>

        <!-- ZAKŁADKA 5: TERMINARZ -->
        <div id="schedule" class="section-view">
            <div class="stream-box">
                <iframe src="https://www.scorebat.com/embed/" style="width:100%; height:600px; border:none;" scrolling="yes"></iframe>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId, btn) {
            document.querySelectorAll('.section-view, .stream-box').forEach(el => {
                if(el.id === tabId || el.id === 'streams' && tabId === 'streams') {
                    el.classList.add('active');
                } else if(el.classList.contains('section-view')) {
                    el.classList.remove('active');
                }
            });
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
        }

        function changeStream(url, btn) {
            document.getElementById('videoPlayer').src = url;
            document.querySelectorAll('.server-btn').forEach(el => el.classList.remove('active'));
            btn.classList.add('active');
        }
    </script>
{% endif %}

</body>
</html>
"""

@bot.message_handler(commands=["14VI40"])
def handle_command(message):
    sent_message = bot.reply_to(
        message,
        "Witaj! Twój panel VIP bet by hrabia jest gotowy: "
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
            error = "Niepoprawne hasło dostępu!"

    logged_in = session.get("authenticated", False)
    return render_template_string(HTML_TEMPLATE, logged_in=logged_in, error=error)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
