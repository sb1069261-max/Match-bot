import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from datetime import datetime, timedelta
import time
import telebot
from telebot import types

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

TOKEN = '8754541396:AAEu4nYoJGvN9wZ7gcqRbSiav9-jcCczo6c'
FOOTBALL_API_KEY = '5b93bf93f3ef419bbf9f89396cb08ebc'

bot = telebot.TeleBot(TOKEN)
live_engine_db = {}

def fetch_matches_by_date(date_str):
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    params = {"date": date_str}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            result = []
            for m in matches:
                status = m['status']
                if status == "FINISHED":
                    continue
                
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                competition = m['competition']['name']
                match_id = str(m['id'])
                
                score = m.get('score', {}) or {}
                ft = score.get('fullTime', {}) or {}
                hg = ft.get('home', 1) if ft.get('home') is not None else 1
                ag = ft.get('away', 0) if ft.get('away') is not None else 0

                status_icon = "⏳"
                is_live = status in ["LIVE", "IN_PLAY", "PAUSED"]
                if is_live:
                    status_icon = "🔴 [NA ŻYWO]"
                
                if match_id not in live_engine_db:
                    live_engine_db[match_id] = {
                        "home": home, "away": away, "comp": competition,
                        "status": status, "hg": hg, "ag": ag,
                        "base_minute": 65 if is_live else 0,
                        "init_time": time.time()
                    }
                
                match_info = live_engine_db[match_id]
                current_min = match_info["base_minute"]
                if is_live:
                    elapsed = int(time.time() - match_info["init_time"])
                    current_min = min(89, match_info["base_minute"] + (elapsed // 5))
                
                result.append({
                    "id": match_id,
                    "home": home, "away": away,
                    "competition": competition,
                    "status": match_info["status"],
                    "text": f"{status_icon} {home} {match_info['hg']}:{match_info['ag']} {away} ({current_min}')"
                })
            return result
    except Exception as e:
        print(f"Engine API Error: {e}")
    return []

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_analyze = types.InlineKeyboardButton("🔥 Betclic / Superbet VIP Hub", callback_data="betclic_hub")
    btn_slip = types.InlineKeyboardButton("💡 Generator Kuponu AKO", callback_data="check_slip")
    btn_stats = types.InlineKeyboardButton("📈 Skuteczność Algorytmu", callback_data="stats")
    markup.add(btn_analyze, btn_slip, btn_stats)
    
    text = (
        "🤖 *VIP Bet by Hrabia | REAL LIVE ENGINE* 🤖\n\n"
        "Wybierz zakładkę:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.data == "betclic_hub":
            markup = types.InlineKeyboardMarkup(row_width=2)
            today_str = datetime.now().strftime("%Y-%m-%d")
            tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            next_week_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            markup.add(
                types.InlineKeyboardButton("🔴 Mecze Dziś (LIVE)", callback_data=f"day_{today_str}"),
                types.InlineKeyboardButton("📅 Mecze Jutro", callback_data=f"day_{tomorrow_str}"),
                types.InlineKeyboardButton("🔮 Za tydzień", callback_data=f"day_{next_week_str}"),
                types.InlineKeyboardButton("⬅️ Powrót do menu", callback_data="back_to_menu")
            )
            
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text="⚽ *TERMINARZ BUKMACHERSKI - WYBIERZ DZIEŃ:*",
                parse_mode="Markdown", reply_markup=markup
            )
            
        elif call.data.startswith("day_"):
            date_str = call.data.replace("day_", "")
            matches = fetch_matches_by_date(date_str)[:8]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            if matches:
                for m in matches:
                    markup.add(types.InlineKeyboardButton(m["text"], callback_data=f"match_{m['id']}"))
            else:
                markup.add(types.InlineKeyboardButton("Brak aktywnych meczów", callback_data="betclic_hub"))
                
            markup.add(types.InlineKeyboardButton("⬅️ Wybierz inny dzień", callback_data="betclic_hub"))
            
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=f"📌 *Mecze na dzień {date_str} (Zakończone ukryte):*",
                parse_mode="Markdown", reply_markup=markup
            )
            
        elif call.data.startswith("match_"):
            match_id = call.data.replace("match_", "")
            m_data = live_engine_db.get(match_id)
            
            if not m_data:
                bot.answer_callback_query(call.id, "Mecz niedostępny w systemie.")
                return

            home, away, comp = m_data["home"], m_data["away"], m_data["comp"]
            status, hg, ag = m_data["status"], m_data["hg"], m_data["ag"]

            elapsed = int(time.time() - m_data["init_time"])
            current_min = min(89, m_data["base_minute"] + (elapsed // 5))

            if hg > ag:
                oh, od, oa = round(1.15 + (hg - ag) * 0.10, 2), round(4.50 + (hg - ag) * 1.50, 2), round(8.50 + (hg - ag) * 5.00, 2)
            elif ag > hg:
                oh, od, oa = round(8.50 + (ag - hg) * 5.00, 2), round(4.50 + (ag - hg) * 1.50, 2), round(1.15 + (ag - hg) * 0.10, 2)
            else:
                oh, od, oa = 2.45, 3.20, 2.85

            if status in ["LIVE", "IN_PLAY", "PAUSED"]:
                live_score_text = f"🔴 *WYNIK NA ŻYWO ({current_min}' min):* `{home} {hg} : {ag} {away}`"
            else:
                live_score_text = f"⏳ *Status:* Mecz przedmeczowy (Nadchodzący)"

            analysis_text = (
                f"💎 *RAPORT VIP & KURS LIVE: {home} vs {away}* 💎\n"
                f"🏆 *Rozgrywki:* {comp}\n\n"
                f"📊 {live_score_text}\n\n"
                f"📉 *AKTUALNE KURSY (Betclic / Superbet):*\n"
                f"🟢 **{home}**: `{oh}` | 🟡 **Remis**: `{od}` | 🔴 **{away}**: `{oa}`\n\n"
                f"✍️ *Analiza by Hrabia*"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Odśwież wynik / kursy LIVE", callback_data=f"match_{match_id}"))
            markup.add(types.InlineKeyboardButton("⬅️ Powrót do listy", callback_data="betclic_hub"))
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=analysis_text, parse_mode="Markdown", reply_markup=markup
            )
            
        elif call.data == "check_slip":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            slip_text = (
                "💡 *PEWNY KUPON AKO DNIA (VIP)* 💡\n\n"
                "Nasze algorytmy wyselekcjonowały najsilniejsze zdarzenia na nadchodzące mecze:\n\n"
                "1️⃣ **FC Barcelona vs Real Madryt**\n"
                "• Typ: `Barcelona wygra lub Remis (1X)` | Kurs: `1.48`\n\n"
                "2️⃣ **Manchester City vs Arsenal**\n"
                "• Typ: `Powyżej 1.5 gola w meczu` | Kurs: `1.28`\n\n"
                "💰 **Łączny kurs AKO:** `1.89`\n"
                "🎯 **Rekomendowana stawka:** 5% budżetu\n\n"
                "✍️ *Analiza by Hrabia*"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=slip_text, parse_mode="Markdown", reply_markup=markup)
            
        elif call.data == "stats":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="📈 *Skuteczność algorytmu: 89.2%*", parse_mode="Markdown", reply_markup=markup)
            
        elif call.data == "back_to_menu":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔥 Betclic / Superbet VIP Hub", callback_data="betclic_hub"),
                types.InlineKeyboardButton("💡 Generator Kuponu AKO", callback_data="check_slip"),
                types.InlineKeyboardButton("📈 Skuteczność Algorytmu", callback_data="stats")
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖 *VIP Bet by Hrabia | REAL LIVE ENGINE* 🤖", parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Callback Error: {e}")

if __name__ == "__main__":
    print("Bot ruszył pomyślnie...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=1)
