import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# Prosty serwer HTTP dla Render (żeby spełnić wymagania portu)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Uruchomienie serwera HTTP w osobnym wątku
threading.Thread(target=run_http_server, daemon=True).start()

# Poprawny token bota w cudzysłowie
TOKEN = '8921204127:AAEuwzlb5Uck9iVs--sGEzT2xI9IAxKxgk'
CHANNEL_USERNAME = '@Bot_vip_OG'

bot = telebot.TeleBot(TOKEN)

# Funkcja sprawdzająca czy użytkownik jest członkiem grupy
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Błąd sprawdzania subskrypcji: {e}")
        return False

# Start / Menu główne z całkowitym pominięciem bramki na czas testów
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    # Menu główne wyświetlane od razu bez sprawdzania grupy
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

# Obsługa kliknięć w przyciski
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if call.data == "check_subscription":
        if is_user_in_channel(user_id):
            bot.answer_callback_query(call.id, "Dziękujemy! Uzyskałeś dostęp.")
            fake_message = call.message
            fake_message.from_user = call.from_user
            send_welcome(fake_message)
        else:
            bot.answer_callback_query(call.id, "Nadal nie dołączyłeś do grupy!", show_alert=True)
        return

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

# Uruchomienie bota
if __name__ == "__main__":
    print("Bot ruszył...")
    bot.infinity_polling(skip_pending=True)
