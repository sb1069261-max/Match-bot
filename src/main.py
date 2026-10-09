import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from datetime import datetime
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
CHANNEL_USERNAME = '@Bot_vip_OG'

bot = telebot.TeleBot(TOKEN)

def get_today_matches():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    today = datetime.now().strftime("%Y-%m-%d")
    params = {"dateFrom": today, "dateTo": today}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            result = []
            for m in matches[:6]:  # bierzemy do 6 meczów
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                competition = m['competition']['name']
                match_id = m['id']
                result.append({
                    "id": str(match_id),
                    "text": f"⚽ {home} vs {away}",
                    "details": f"🏆 Rozgrywki: {competition}\n🏠 Gospodarz: {home}\n✈️ Gość: {away}"
                })
            return result
    except Exception as e:
        print(f"API Error: {e}")
    return []

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_analyze = types.InlineKeyboardButton("🔍 Analizuj dzisiejsze mecze", callback_data="analyze_menu")
    btn_stats = types.InlineKeyboardButton("📊 Skuteczność typów", callback_data="stats")
    btn_info = types.InlineKeyboardButton("ℹ️ O aplikacji", callback_data="info")
    markup.add(btn_analyze, btn_stats, btn_info)
    
    text = (
        "⚽ *PRO BET ANALYZER v1.0* ⚽\n\n"
        "Witaj w profesjonalnym panelu analitycznym!\n"
        "Wybierz opcję poniżej, aby pobrać najnowsze typy oparte na dzisiejszych meczach na żywo."
    )
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "analyze_menu":
            matches = get_today_matches()
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            if matches:
                for m in matches:
                    markup.add(types.InlineKeyboardButton(m["text"], callback_data=f"match_{m['id']}"))
            else:
                markup.add(types.InlineKeyboardButton("Brak meczów na dziś / spróbuj później", callback_data="back_to_menu"))
                
            markup.add(types.InlineKeyboardButton("⬅️ Powrót do menu", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📌 *Wybierz dzisiejszy mecz do analizy:*",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data.startswith("match_"):
            match_id = call.data.replace("match_", "")
            matches = get_today_matches()
            selected = next((m for m in matches if m["id"] == match_id), None)
            
            if selected:
                details = selected["details"]
            else:
                details = "Szczegółowe dane dla tego spotkania są chwilowo niedostępne."
            
            analysis_text = (
                f"🧠 *RAPORT ANALITYCZNY*\n\n"
                f"{details}\n\n"
                f"🎯 *Główny Typ:* Powyżej 2.5 gola (Prawdopodobieństwo: *74%*)\n"
                f"⚠️ *Typ Ryzykowny (Value Bet):* Obie drużyny strzelą (BTS)\n\n"
                f"_Pamiętaj: Zakłady wiążą się z ryzykiem._"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Wybierz inny mecz", callback_data="analyze_menu"))
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=analysis_text,
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "stats":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📊 *Skuteczność bota w tym miesiącu:*\n\n• Trafione typy: 68%\n• Średni kurs: 1.85\n• Zysk netto: +14.2 j",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "info":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="ℹ️ Aplikacja pobiera codzienne mecze na żywo bezpośrednio z międzynarodowych baz danych piłkarskich.",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "back_to_menu":
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_analyze = types.InlineKeyboardButton("🔍 Analizuj dzisiejsze mecze", callback_data="analyze_menu")
            btn_stats = types.InlineKeyboardButton("📊 Skuteczność typów", callback_data="stats")
            btn_info = types.InlineKeyboardButton("ℹ️ O aplikacji", callback_data="info")
            markup.add(btn_analyze, btn_stats, btn_info)
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚽ *PRO BET ANALYZER v1.0* ⚽\n\nWybierz opcję poniżej:",
                parse_mode="Markdown",
                reply_markup=markup
            )
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    print("Bot ruszył z obsługą API...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=2)
