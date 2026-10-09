import os
import threading
from flask import Flask, render_template_string, jsonify
import telebot
from telebot import types

# Konfiguracja serwera WWW dla Telegram Mini App
app = Flask(__name__)

TOKEN = '8754541396:AAEu4nYoJGvN9wZ7gcqRbSiav9-jcCczo6c'
bot = telebot.TeleBot(TOKEN)

# Szablon interfejsu Web App (Styl Betclic / Superbet z płynnym licznikiem i kursami LIVE)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIP Bet by Hrabia - Live</title>
    <style>
        body { background-color: #0d1117; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 15px; }
        h2 { text-align: center; color: #e53935; text-transform: uppercase; font-size: 20px; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #8c959f; font-size: 12px; margin-bottom: 20px; }
        .tabs { display: flex; gap: 8px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }
        .tab { background: #21262d; border: none; color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 13px; cursor: pointer; white-space: nowrap; font-weight: bold; }
        .tab.active { background: #e53935; }
        .match-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 12px; margin-bottom: 12px; cursor: pointer; transition: 0.2s; }
        .match-card:hover { border-color: #e53935; }
        .match-header { display: flex; justify-content: space-between; font-size: 11px; color: #8c959f; margin-bottom: 8px; }
        .live-badge { background: #e53935; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        .teams-score { display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: bold; margin-bottom: 10px; }
        .score-box { background: #21262d; padding: 4px 10px; border-radius: 6px; font-family: monospace; color: #f0f6fc; }
        .odds-container { display: flex; gap: 6px; }
        .odd-btn { flex: 1; background: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 6px; text-align: center; color: #fff; font-size: 12px; }
        .odd-value { color: #f1e05a; font-weight: bold; font-size: 13px; }
        .view-section { display: none; }
        .view-section.active { display: block; }
        .back-btn { background: #30363d; border: none; color: white; padding: 8px 12px; border-radius: 6px; margin-bottom: 15px; cursor: pointer; font-size: 13px; }
        .analysis-box { background: #161b22; border-radius: 12px; padding: 15px; border: 1px solid #30363d; }
    </style>
</head>
<body>

    <h2>🔥 VIP Bet by Hrabia Hub</h2>
    <div class="subtitle">Oficjalny Terminal Live & Bukmacherka</div>

    <!-- Zakładki główne -->
    <div id="main-menu" class="view-section active">
        <div class="tabs">
            <button class="tab active" onclick="switchTab('today')">🔴 Mecze Dziś (LIVE)</button>
            <button class="tab" onclick="switchTab('tomorrow')">📅 Mecze Jutro</button>
            <button class="tab" onclick="switchTab('slip')">💡 Generator AKO</button>
        </div>

        <div id="matches-list">
            <!-- Tutaj ładowane są mecze przez JS -->
        </div>
    </div>

    <!-- Widok szczegółów meczu -->
    <div id="match-detail" class="view-section">
        <button class="back-btn" onclick="backToMenu()">⬅️ Powrót do listy</button>
        <div class="analysis-box" id="detail-content">
            <!-- Dynamiczna analiza meczu -->
        </div>
    </div>

    <!-- Widok generatora kuponów -->
    <div id="slip-view" class="view-section">
        <button class="back-btn" onclick="backToMenu()">⬅️ Powrót do menu</button>
        <div class="analysis-box">
            <h3>💡 PEWNY KUPON AKO DNIA (VIP)</h3>
            <p>1️⃣ <b>FC Barcelona vs Real Madryt</b><br>Typ: <code>Barcelona wygra lub Remis (1X)</code> | Kurs: <b>1.48</b></p>
            <p>2️⃣ <b>Manchester City vs Arsenal</b><br>Typ: <code>Powyżej 1.5 gola</code> | Kurs: <b>1.28</b></p>
            <hr style="border-color: #30363d;">
            <p>💰 <b>Łączny kurs AKO:</b> <span style="color: #f1e05a; font-size: 16px;">1.89</span></p>
            <p>🎯 <b>Zalecana stawka:</b> 5% budżetu</p>
            <p style="color: #8c959f; font-size: 11px; margin-top: 15px;">Analiza by Hrabia</p>
        </div>
    </div>

    <script>
        let currentTab = 'today';
        let selectedMatch = null;

        const mockMatches = {
            today: [
                { id: 1, home: "Sporting Braga", away: "Sporting Lizbona", comp: "Liga Betclic", minute: 70, hg: 1, ag: 1, oh: 5.00, od: 1.88, oa: 2.70 },
                { id: 2, home: "Borussia Dortmund", away: "Werder Brema", comp: "Bundesliga", minute: 90, hg: 2, ag: 2, oh: 10.50, od: 1.04, oa: 20.0 },
                { id: 3, home: "Real Madryt", away: "FC Barcelona", comp: "La Liga", minute: 34, hg: 1, ag: 0, oh: 1.85, od: 3.50, oa: 4.10 }
            ],
            tomorrow: [
                { id: 4, home: "Arsenal", away: "Chelsea", comp: "Premier League", minute: 0, hg: 0, ag: 0, oh: 2.10, od: 3.40, oa: 3.30 },
                { id: 5, home: "Bayern Monachium", away: "RB Leipzig", comp: "Bundesliga", minute: 0, hg: 0, ag: 0, oh: 1.45, od: 4.80, oa: 6.20 }
            ]
        };

        // Live zegar w tle (minuty rosną same sekunda po sekundzie jak na Betclic!)
        setInterval(() => {
            mockMatches.today.forEach(m => {
                if (m.minute > 0 && m.minute < 90) {
                    m.minute += 1; // Symulacja upływu czasu
                }
            });
            if (document.getElementById('main-menu').classList.contains('active')) {
                renderMatches();
            }
        }, 10000); // Co 10 sekund minuta rośnie dla realizmu

        function switchTab(tab) {
            if(tab === 'slip') {
                document.getElementById('main-menu').classList.remove('active');
                document.getElementById('match-detail').classList.remove('active');
                document.getElementById('slip-view').classList.add('active');
                return;
            }
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            renderMatches();
        }

        function renderMatches() {
            const list = document.getElementById('matches-list');
            list.innerHTML = '';
            const matches = mockMatches[currentTab] || [];
            
            matches.forEach(m => {
                let statusText = m.minute > 0 ? `<span class="live-badge">🔴 LIVE (${m.minute}')</span>` : `<span style="color:#8c959f;">⏳ Zaplanowany</span>`;
                let card = document.createElement('div');
                card.className = 'match-card';
                card.onclick = () => showDetail(m);
                card.innerHTML = `
                    <div class="match-header">
                        <span>${m.comp}</span>
                        ${statusText}
                    </div>
                    <div class="teams-score">
                        <span>${m.home} vs ${m.away}</span>
                        <div class="score-box">${m.hg} : ${m.ag}</div>
                    </div>
                    <div class="odds-container">
                        <div class="odd-btn">1: <span class="odd-value">${m.oh}</span></div>
                        <div class="odd-btn">X: <span class="odd-value">${m.od}</span></div>
                        <div class="odd-btn">2: <span class="odd-value">${m.oa}</span></div>
                    </div>
                `;
                list.appendChild(card);
            });
        }

        function showDetail(m) {
            selectedMatch = m;
            document.getElementById('main-menu').classList.remove('active');
            document.getElementById('slip-view').classList.remove('active');
            document.getElementById('match-detail').classList.add('active');

            let detail = document.getElementById('detail-content');
            detail.innerHTML = `
                <h3 style="margin-top:0; color:#f0f6fc;">💎 ${m.home} vs ${m.away}</h3>
                <p style="color:#8c959f; font-size:12px;">🏆 Rozgrywki: ${m.comp}</p>
                <div style="background:#21262d; padding:10px; border-radius:8px; text-align:center; font-size:18px; font-weight:bold; margin: 15px 0;">
                    🔴 WYNIK LIVE (${m.minute}' min): ${m.hg} : ${m.ag}
                </div>
                <p>📉 <b>Aktualne kursy bukmacherskie LIVE:</b></p>
                <div class="odds-container" style="margin-bottom: 20px;">
                    <div class="odd-btn">1 (${m.home}): <span class="odd-value">${m.oh}</span></div>
                    <div class="odd-btn">X (Remis): <span class="odd-value">${m.od}</span></div>
                    <div class="odd-btn">2 (${m.away}): <span class="odd-value">${m.oa}</span></div>
                </div>
                <p>🎯 <b>Rekomendacja algorytmu:</b><br>Obserwuj posiadanie piłki i xG. Kurs na bramkę w końcówce mocno rośnie!</p>
                <p style="color:#8c959f; font-size:11px; margin-top:20px; text-align:right;">Analiza by Hrabia</p>
            `;
        }

        function backToMenu() {
            document.getElementById('match-detail').classList.remove('active');
            document.getElementById('slip-view').classList.remove('active');
            document.getElementById('main-menu').classList.add('active');
            renderMatches();
        }

        // Inicjalizacja startowa
        renderMatches();
    </script>
</body>
</html>
"""

@app.route('/')
def web_app():
    return render_template_string(HTML_TEMPLATE)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Uruchomienie serwera WWW w osobnym wątku
threading.Thread(target=run_flask, daemon=True).start()

# Obsługa bota Telegram – przycisk otwierający aplikację Web App
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Tworzymy przycisk Web App, który otwiera aplikację bezpośrednio w Telegramie!
    web_app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://twoja-aplikacja.onrender.com")
    btn_webapp = types.InlineKeyboardButton("🔥 Otwórz Terminal Betclic LIVE", web_app=types.WebAppInfo(url=web_app_url))
    
    markup.add(btn_webapp)
    
    text = (
        "🤖 *VIP Bet by Hrabia | WEB APP ENGINE* 🤖\n\n"
        "Kliknij przycisk poniżej, aby uruchomić profesjonalny terminal żywych kursów i wyników na żywo bezpośrednio w Telegramie:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

if __name__ == "__main__":
    print("Telegram Mini App Bot ruszył pomyślnie...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=1)
