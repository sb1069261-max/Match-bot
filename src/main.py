import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# Token w cudzysłowie
TOKEN = '8921204127:AAEhREAu09w-xlbY8JZjKXyGul3ct3RRS4'
CHANNEL_USERNAME = '@Bot_vip_OG'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    banner_url = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?q=80&w=1000&auto=format&fit=crop"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_analyze = types.InlineKeyboardButton("🔍 Analizuj dzisiejsze mecze", callback_data="analyze_menu")
    btn_stats = types.InlineKeyboardButton("📊 Skuteczność typów", callback_data="stats")
    btn_info = types.InlineKeyboardButton("ℹ️ O aplikacji", callback_data="info")
    markup.add(btn_analyze, btn_stats, btn_info)
    
    caption = (
        "⚽ *PRO BET ANALYZER v1.0* ⚽\n\n"
        "Witaj w profesjonalnym panelu analitycznym!\n"
        "Wybierz opcję poniżej, aby wygenerować najnowsze typy bukmacherskie oparte na statystykach."
    )
    
    bot.send_photo(message.chat.id, banner_url, caption=caption, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "analyze_menu":
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_m1 = types.InlineKeyboardButton("🔥 Real Madryt vs Barcelona", callback_data="match_1")
            btn_m2 = types.InlineKeyboardButton("⚡ Manchester City vs Arsenal", callback_data="match_2")
            btn_back = types.InlineKeyboardButton("⬅️ Powrót do menu", callback_data="back_to_menu")
            markup.add(btn_m1, btn_m2, btn_back)
            
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="📌 *Wybierz mecz do szczegółowej analizy:*",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data in ["match_1", "match_2"]:
            match_name = "Real Madryt vs Barcelona" if call.data == "match_1" else "Manchester City vs Arsenal"
            
            analysis_text = (
                f"🧠 *RAPORT ANALITYCZNY: {match_name}*\n\n"
                f"📈 *Sytuacja drużyn:* Ostatnia forma gospodarzy jest stabilna, goście radzą sobie dobrze na wyjazdach.\n"
                f"🎯 *Główny Typ:* Powyżej 2.5 gola (Prawdopodobieństwo: *78%*)\n"
                f"⚠️ *Typ Ryzykowny (Value Bet):* Remis do przerwy (Kurs ok. 2.15)\n\n"
                f"_Pamiętaj: Zakłady wiążą się z ryzykiem._"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Wybierz inny mecz", callback_data="analyze_menu"))
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=analysis_text,
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "stats":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="📊 *Skuteczność bota w tym miesiącu:*\n\n• Trafione typy: 68%\n• Średni kurs: 1.85\n• Zysk netto: +14.2 j",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "info":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Menu główne", callback_data="back_to_menu"))
            
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="ℹ️ Aplikacja stworzona jako automatyczny analityk statystyczny oparty na algorytmach sztucznej inteligencji.",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif call.data == "back_to_menu":
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_analyze = types.InlineKeyboardButton("🔍 Analizuj dzisiejsze mecze", callback_data="analyze_menu")
            btn_stats = types.InlineKeyboardButton("📊 Skuteczność typów", callback_data="stats")
            btn_info = types.InlineKeyboardButton("ℹ️ O aplikacji", callback_data="info")
            markup.add(btn_analyze, btn_stats, btn_info)
            
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="⚽ *PRO BET ANALYZER v1.0* ⚽\n\nWybierz opcję poniżej:",
                parse_mode="Markdown",
                reply_markup=markup
            )
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    print("Bot ruszył...")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=2)
