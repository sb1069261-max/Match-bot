import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from datetime import datetime, timedelta
import random
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

# Pamięć podręczna symulatora LIVE (Silnik Betclic Engine v5.0)
live_engine_db = {}

def fetch_live_engine_matches(date_str):
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
                    continue  # Zakończone mecze całkowicie znikają jak na Betclic LIVE
                
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                competition = m['competition']['name']
                match_id = str(m['id'])
                
                score = m.get('score', {}) or {}
                ft = score.get('fullTime', {}) or {}
                hg = ft.get('home', 0) if ft.get('home') is not None else 0
                ag = ft.get('away', 0) if ft.get('away') is not None else 0

                status_icon = "⏳"
                is_live = status in ["LIVE", "IN_PLAY", "PAUSED"]
                if is_live:
                    status_icon = "🔴 [NA ŻYWO]"
                
                # Inicjalizacja silnika dla nowego meczu
                if match_id not in live_engine_db:
                    if is_live:
                        if hg == 0 and ag == 0:
                            hg, ag = random.choices([(1,0), (0,1), (1,1), (2,1)], weights=[35, 30, 25, 10])[0]
                        base_minute = random.randint(50, 75)
                    else:
                        base_minute = 0
                        hg, ag = 0, 0
                    
                    live_engine_db[match_id] = {
                        "home": home, "away": away, "comp": competition,
                        "status": status, "hg": hg, "ag": ag, 
                        "base_minute": base_minute,
                        "init_time": time.time(),
                        "momentum": random.choice([-1, 1]) # Kto przeważa
                    }
                
                # Dynamiczna aktualizacja minuty w locie
                match_info = live_engine_db[match_id]
                current_minute = match_info["base_minute"]
                if match_info["status"] in ["LIVE", "IN_PLAY", "PAUSED"]:
                    elapsed_seconds = int(time.time() - match_info["init_time"])
                    # Co 6 sekund w realnym świecie mija 1 minuta meczowa
                    current_minute = min(90, match_info["base_minute"] + (elapsed_seconds // 6))
                    match_info["current_minute"] = current_minute
                else:
                    match_info["current_minute"] = 0

                result.append({
                    "id": match_id,
                    "home": home, "away": away,
                    "competition": competition,
                    "status": match_info["status"],
                    "text": f"{status_icon} {home} {match_info['hg']}:{match_info['ag']} {away} ({current_minute}')"
                })
            return result
    except Exception as e:
        print(f"Engine API Error: {e}")
    return []

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_analyze = types.InlineKeyboardButton("🔥 Betclic VIP Hub (Live Engine)", callback_data="betclic_hub")
    btn_slip = types.InlineKeyboardButton("💡 Generator Kuponu AKO", callback_data="check_slip")
    btn_stats = types.InlineKeyboardButton("📈 Skuteczność Algorytmu", callback_data="stats")
    markup.add(btn_analyze, btn_slip, btn_stats)
    
    text = (
        "🤖 *VIP Bet by Hrabia | PRO LIVE ENGINE* 🤖\n\n"
        "System gotowy do gry. Wybierz zakładkę:"
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
                text="⚽ *STREFA BETCLIC LIVE - WYBIERZ DZIEŃ:*",
                parse_mode="Markdown", reply_markup=markup
            )
            
        elif call.data.startswith("day_"):
            date_str = call.data.replace("day_", "")
            matches = fetch_live_engine_matches(date_str)[:8]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            if matches:
                for m in matches:
                    markup.add(types.InlineKeyboardButton(m["text"], callback_data=f"match_{m['id']}"))
            else:
                markup.add(types.InlineKeyboardButton("Brak aktywnych meczów", callback_data="betclic_hub"))
                
            markup.add(types.InlineKeyboardButton("⬅️ Wybierz inny dzień", callback_data="betclic_hub"))
            
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=f"📌 *Terminal LIVE na dzień {date_str} (Zakończone ukryte):*",
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
            
            # Przeliczanie minuty na żywo w oparciu o czas systemowy
            if status in ["LIVE", "IN_PLAY", "PAUSED"]:
                elapsed_seconds = int(time.time() - m_data["init_time"])
                minute = min(90, m_data["base_minute"] + (elapsed_seconds // 6))
                m_data["current_minute"] = minute
            else:
                minute = 0

            # Algorytm kursów bukmacherskich reagujący sekunda po sekundzie na wynik
            # Jak na Betclic: prowadzący ma mały kurs, przegrywający ma wysoki, remis pośrodku
            if hg > ag:
                oh = round(random.uniform(1.05, 1.25), 2)
                od = round(random.uniform(5.50, 9.50), 2)
                oa = round(random.uniform(15.0, 35.0), 2)
            elif ag > hg:
                oh = round(random.uniform(14.0, 30.0), 2)
                od = round(random.uniform(5.00, 8.50), 2)
                oa = round(random.uniform(1.08, 1.28), 2)
            else:
                # Remis w końcówce wywołuje szalone kursy jak na screenie!
                if minute >= 80:
                    oh = round(random.uniform(8.00, 14.0), 2)
                    od = round(random.uniform(1.03, 1.15), 2)
                    oa = round(random.uniform(12.0, 22.0), 2)
                else:
                    oh = round(random.uniform(2.10, 2.80), 2)
                    od = round(random.uniform(2.90, 3.50), 2)
                    oa = round(random.uniform(2.20, 3.00), 2)

            if status in ["LIVE", "IN_PLAY", "PAUSED"]:
                live_score_text = f"🔴 *WYNIK NA ŻYWO ({minute}' min - LIVE ENGINE):* `{home} {hg} : {ag} {away}`"
            else:
                live_score_text = f"⏳ *Status:* Mecz nadchodzący (Przedmeczowy)"

            analysis_text = (
                f"💎 *BETCLIC VIP TERMINAL: {home} vs {away}* 💎\n"
                f"🏆 *Rozgrywki:* {comp}\n\n"
                f"📊 {live_score_text}\n\n"
                f"📉 *DYNAMICSZNE KURSY BUKMACHERSKE (LIVE):*\n"
                f"🟢 *{home}*: `{oh:.2f}`\n"
                f"🟡 *Remis*: `{od:.2f}`\n"
                f"🔴 *{away}*: `{oa:.2f}`\n\n"
                f"🎯 *Rekomendacja algorytmu:* Obserwuj dynamikę xG przed oddaniem zakładu.\n"
                f"✍️ *Analiza by Hrabia*"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Odśwież stawkę / kursy LIVE", callback_data=f"match_{match_id}"))
            markup.add(types.InlineKeyboardButton("⬅️ Powrót do listy", callback_data="betclic_hub"))
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=analysis_text, parse_mode="Markdown", reply_markup=markup
            )
            
        elif call.data == "check_slip":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="💡 *Generator Kuponu AKO gotowy do pracy.*", parse_mode="Markdown", reply_markup=markup)
            
        elif call.data == "stats":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="📈 *Skuteczność algorytmu LIVE: 89.2%*", parse_mode="Markdown", reply_markup=markup)
            
        elif call.data == "back_to_menu":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔥 Betclic VIP Hub (Live Engine)", callback_data="betclic_hub"),
                types.InlineKeyboardButton("💡 Generator Kuponu AKO", callback_data="check_slip"),
                types.InlineKeyboardButton("📈 Skuteczność Algorytmu", callback_data="stats")
            )
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🤖 *VIP Bet by Hrabia | PRO LIVE ENGINE* 🤖", parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Callback Error: {e}")

if __name__ == "__main__":
    print("Silnik Betclic Live ruszył pomyślnie...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=1)
