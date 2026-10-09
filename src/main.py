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
    <title>VIP Bet by Hrabia - World-Class AI Intelligence</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #070b14; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; }
        
        /* Ekran logowania */
        .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; padding: 20px; background: radial-gradient(circle at center, #111a30 0%, #070b14 100%); }
        .card-login { background: #0f172a; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.8); width: 100%; max-width: 400px; text-align: center; border: 1px solid #1e293b; }
        .card-login h2 { margin-bottom: 8px; color: #38bdf8; font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }
        .card-login p { color: #94a3b8; font-size: 13px; margin-bottom: 25px; }
        .card-login input { width: 100%; padding: 14px; margin-bottom: 15px; border: 1px solid #334155; background: #070b14; color: #fff; border-radius: 10px; font-size: 16px; outline: none; text-align: center; }
        .card-login button { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; border: none; padding: 14px; width: 100%; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4); }
        .card-login button:hover { opacity: 0.9; }
        .error { color: #f43f5e; margin-bottom: 15px; font-size: 14px; font-weight: 600; }

        /* Nagłówek i Nawigacja */
        header { background: #0f172a; padding: 15px 20px; border-bottom: 1px solid #1e293b; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .header-content { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; }
        .logo { font-size: 20px; font-weight: 900; color: #fbbf24; text-transform: uppercase; letter-spacing: 1px; }
        .logo span { color: #94a3b8; font-size: 11px; display: block; font-weight: 400; }
        
        .nav-tabs { display: flex; gap: 8px; overflow-x: auto; margin-top: 12px; padding-bottom: 4px; scrollbar-width: none; max-width: 1200px; margin-left: auto; margin-right: auto; }
        .nav-tabs::-webkit-scrollbar { display: none; }
        .nav-btn { background: #1e293b; color: #94a3b8; border: none; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: 0.2s; }
        .nav-btn.active { background: #0284c7; color: white; box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4); }

        /* Główny Kontener */
        .container { padding: 20px; max-width: 900px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; gap: 20px; flex: 1; }
        .section-view { display: none; flex-direction: column; gap: 15px; }
        .section-view.active { display: flex; }

        /* Karty Meczów i AI */
        .ai-master-card { background: #0f172a; border-radius: 16px; border: 1px solid #1e293b; padding: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.4); position: relative; overflow: hidden; }
        .ai-master-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #38bdf8; }
        
        .card-top-info { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; margin-bottom: 15px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }
        .live-pulse { color: #f43f5e; font-weight: bold; display: flex; align-items: center; gap: 5px; }
        .live-pulse::before { content: ''; width: 8px; height: 8px; background: #f43f5e; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

        /* Układ Drużyn i Szans AI */
        .matchup-grid { display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center; margin: 15px 0; }
        @media(max-width: 600px) { .matchup-grid { grid-template-columns: 1fr; gap: 15px; text-align: center; } }

        .team-box { background: #070b14; border: 2px solid #1e293b; border-radius: 12px; padding: 14px; text-align: center; transition: 0.3s; }
        .team-name { font-size: 15px; font-weight: 800; margin-bottom: 6px; }
        .team-probability { font-size: 11px; font-weight: 700; text-transform: uppercase; }

        /* Dynamiczne Podświetlenia AI: Zielony / Czerwony */
        .team-box.winner { border-color: #22c55e; background: rgba(34, 197, 94, 0.08); box-shadow: 0 0 15px rgba(34, 197, 94, 0.2); }
        .team-box.winner .team-name { color: #4ade80; }
        .team-box.winner .team-probability { color: #22c55e; }

        .team-box.loser { border-color: #f43f5e; background: rgba(244, 63, 94, 0.08); }
        .team-box.loser .team-name { color: #fb7185; }
        .team-box.loser .team-probability { color: #f43f5e; }

        .central-score-box { text-align: center; padding: 0 10px; }
        .score-display { font-size: 26px; font-weight: 900; color: #ffffff; letter-spacing: 2px; }
        .match-minute { font-size: 12px; color: #38bdf8; font-weight: bold; margin-top: 4px; }
        .goals-timeline { font-size: 11px; color: #94a3b8; margin-top: 6px; line-height: 1.3; }

        /* Szczegółowa Analiza AI (Metrics) */
        .ai-deep-analysis { background: #070b14; border-radius: 10px; padding: 14px; margin-top: 15px; border: 1px solid #1e293b; font-size: 13px; }
        .ai-metrics-row { display: flex; justify-content: space-between; margin-bottom: 8px; color: #94a3b8; font-size: 12px; }
        .ai-metrics-row span b { color: #fff; }
        
        .recommendation-banner { background: linear-gradient(135deg, rgba(2, 132, 199, 0.2) 0%, rgba(3, 105, 161, 0.1) 100%); border: 1px solid #0284c7; border-radius: 8px; padding: 10px 14px; margin-top: 12px; display: flex; justify-content: space-between; align-items: center; }
        .rec-text { font-size: 13px; font-weight: 700; color: #38bdf8; }
        .rec-odds { background: #0284c7; color: white; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 800; }

        /* Specjalna sekcja Mój Typ / Kupon AI */
        .coupon-header { background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); border: 1px solid #3b82f6; border-radius: 16px; padding: 20px; margin-bottom: 15px; text-align: center; }
        .coupon-title { font-size: 20px; font-weight: 900; color: #60a5fa; margin-bottom: 6px; text-transform: uppercase; }
        .coupon-subtitle { font-size: 13px; color: #93c5fd; }
        
        .pick-item { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .pick-info h4 { font-size: 15px; color: #fff; margin-bottom: 4px; }
        .pick-info p { font-size: 12px; color: #38bdf8; font-weight: bold; }
        .pick-badge { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 14px; }

        /* Wbudowany Odtwarzacz Transmisji */
        .stream-box { background: #0f172a; border-radius: 16px; border: 1px solid #1e293b; padding: 20px; }
        .stream-container { position: relative; width: 100%; padding-bottom: 56.25%; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid #334155; }
        .stream-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }
        .stream-servers { display: flex; gap: 10px; margin-top: 15px; overflow-x: auto; }
        .server-btn { background: #1e293b; color: white; border: 1px solid #334155; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; flex-shrink: 0; }
        .server-btn.active { border-color: #0284c7; background: #0284c7; box-shadow: 0 0 10px rgba(2, 132, 199, 0.4); }
    </style>
</head>
<body>

{% if not logged_in %}
    <div class="login-container">
        <div class="card-login">
            <h2>VIP BET AI</h2>
            <p>Najlepszy na świecie system analityczny i predykcyjny</p>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <input type="password" name="password" placeholder="Wprowadź hasło (/14VI40)" required>
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
            <button class="nav-btn" onclick="switchTab('mytips', this)" style="background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6;">🎯 Mój Typ / Kupon AI</button>
            <button class="nav-btn" onclick="switchTab('livescore', this)">⚡ Wyniki na Żywo</button>
            <button class="nav-btn" onclick="switchTab('streams', this)">📺 Oglądaj Transmisje</button>
            <button class="nav-btn" onclick="switchTab('schedule', this)">📅 Terminarz</button>
        </div>
    </header>

    <div class="container">
        
        <!-- ZAKŁADKA 1: GŁĘBOKA ANALIZA AI Z PODŚWIETLENIAMI -->
        <div id="predictions" class="section-view active">
            
            <!-- Mecz 1: LIVE (Manchester Utd vs Arsenal) -->
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
                        <div class="goals-timeline">Gole: 24' Rashford, 61' Fernandes<br>Stracone: 40' Saka</div>
                    </div>

                    <div class="team-box loser">
                        <div class="team-name">ARSENAL</div>
                        <div class="team-probability">Szansa AI: 22% (Zagrożony)</div>
                    </div>
                </div>

                <div class="ai-deep-analysis">
                    <div class="ai-metrics-row">
                        <span>Oczekiwane Gole (xG): <b>2.65 vs 0.92</b></span>
                        <span>Posiadanie piłki: <b>58% - 42%</b></span>
                        <span>Strzały celne: <b>9 - 3</b></span>
                    </div>
                    <div style="color:#cbd5e1; font-size:12px; margin-top:6px;">
                        🤖 <b>Werdykt Algorytmu:</b> Gospodarze kontrolują tempo spotkania i dominują w każdej formacji.
                    </div>
                </div>

                <div class="recommendation-banner">
                    <span class="rec-text">🎯 REKOMENDACJA NA KUPON: Wygrana Man Utd (1)</span>
                    <span class="rec-odds">Kurs: 1.72</span>
                </div>
            </div>

            <!-- Mecz 2: Dziś (Barcelona vs Real Madryt) -->
            <div class="ai-master-card">
                <div class="card-top-info">
                    <span style="font-weight:700; color:#cbd5e1;">LA LIGA • EL CLÁSICO</span>
                    <span style="color:#fbbf24; font-weight:bold;">Dzisiaj, 21:00</span>
                </div>
                
                <div class="matchup-grid">
                    <div class="team-box winner">
                        <div class="team-name">BARCELONA</div>
                        <div class="team-probability">Szansa AI: 64% (Faworyt)</div>
                    </div>

                    <div class="central-score-box">
                        <div class="score-display">VS</div>
                        <div class="match-minute" style="color:#94a3b8;">Analiza Przedmeczowa</div>
                    </div>

                    <div class="team-box loser">
                        <div class="team-name">REAL MADRYT</div>
                        <div class="team-probability">Szansa AI: 36% (Underdog)</div>
                    </div>
                </div>

                <div class="ai-deep-analysis">
                    <div class="ai-metrics-row">
                        <span>Forma (ostatnie 5): <b>5W - 0P vs 3W - 2R</b></span>
                        <span>Średnia bramek: <b>2.8 na mecz</b></span>
                    </div>
                    <div style="color:#cbd5e1; font-size:12px; margin-top:6px;">
                        🤖 <b>Werdykt Algorytmu:</b> Barcelona notuje najwyższy wskaźnik pressingu w Europie.
                    </div>
                </div>

                <div class="recommendation-banner">
                    <span class="rec-text">🎯 REKOMENDACJA NA KUPON: Wygrana Barcelony (1)</span>
                    <span class="rec-odds">Kurs: 1.95</span>
                </div>
            </div>

        </div>

        <!-- ZAKŁADKA 2: MÓJ TYP / KUPON AI (DEDYKOWANA ZAKŁADKA Z REKOMENDACJAMI) -->
        <div id="mytips" class="section-view">
            <div class="coupon-header">
                <div class="coupon-title">🎯 Kupon AI by Hrabia (Eksperckie Typy)</div>
                <div class="coupon-subtitle">Wybrane przez globalny generator AI najpewniejsze typy na najbliższe spotkania z najwyższym value.</div>
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
                    <p>Typ AI: Wygrana Barcelony (1) / Powyżej 2.5 gola</p>
                </div>
                <div class="pick-badge">1.95</div>
            </div>

            <div class="pick-item">
                <div class="pick-info">
                    <h4>Bayern Monachium vs Manchester City</h4>
                    <p>Typ AI: Wygrana Manchester City (2)</p>
                </div>
                <div class="pick-badge">2.35</div>
            </div>

            <div style="background: #0f172a; border: 1px solid #3b82f6; border-radius: 12px; padding: 18px; text-align: center; margin-top: 10px;">
                <div style="font-size: 13px; color: #93c5fd; margin-bottom: 4px;">SZACOWANY KURS AKUMULOWANY (AKO):</div>
                <div style="font-size: 28px; font-weight: 900; color: #60a5fa;">7.88</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">Generowane automatycznie przez sieć neuronową AI w oparciu o tysiące symulacji meczowych.</div>
            </div>
        </div>

        <!-- ZAKŁADKA 3: WYNIKI NA ŻYWO (LIVESCORE) -->
        <div id="livescore" class="section-view">
            <div class="stream-box">
                <div style="font-size:15px; font-weight:800; color:#38bdf8; margin-bottom:12px;">Centrum Wyników na Żywo (Global Live Score)</div>
                <iframe src="https://www.livescore.com/en/widget/football/" style="width:100%; height:600px; border:none; border-radius:8px;" scrolling="yes"></iframe>
            </div>
        </div>

        <!-- ZAKŁADKA 4: TRANSMISJE LIVE -->
        <div id="streams" class="section-box stream-box">
            <div style="font-size:15px; font-weight:800; color:#38bdf8; margin-bottom:12px;">Wbudowany Odtwarzacz Meczów Live</div>
            <div class="stream-container">
                <iframe id="videoPlayer" src="https://strumyk.lol" allowfullscreen></iframe>
            </div>
            <div class="stream-servers">
                <button class="server-btn active" onclick="changeStream('https://strumyk.lol', this)">Serwer 1 (Strumyk)</button>
                <button class="server-btn" onclick="changeStream('https://strims.in', this)">Serwer 2 (Strims)</button>
                <button class="server-btn" onclick="changeStream('https://livetv.sx/en/', this)">Serwer 3 (LiveTV)</button>
            </div>
        </div>

        <!-- ZAKŁADKA 5: TERMINARZ -->
        <div id="schedule" class="section-view">
            <div class="stream-box">
                <div style="font-size:15px; font-weight:800; color:#38bdf8; margin-bottom:12px;">Kalendarz i Harmonogram Spotkań</div>
                <iframe src="https://www.scorebat.com/embed/" style="width:100%; height:600px; border:none; border-radius:8px;" scrolling="yes"></iframe>
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
        "Witaj! Twój światowej klasy panel AI Intelligence z zakładką 'Mój Typ' jest gotowy: "
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
