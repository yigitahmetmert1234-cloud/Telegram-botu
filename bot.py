import os
import random
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- AYARLAR ---
TOKEN = '8071326897:AAF5tqcTz7SxDulJ8nskD6rftIoqvQ46mZo' # BotFather'dan aldığın token
GOD_IDS = [8696460554] # Kendi Telegram ID'n
DB_FILE = "database.json"

# --- RENDER İÇİN ÖZEL WEB SUNUCU (Hata Almamak İçin Şart) ---
def run_web_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Aktif!")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Web sunucusu {port} portunda baslatildi...")
    server.serve_forever()

# --- VERİTABANI ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

user_data = load_db()

def get_user(user_id):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {"balance": 1000, "last_mine": 0}
    return user_data[uid]

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 Bot Calisiyor!\n/cuzdan\n/maden\n/slot <miktar>")

async def cuzdan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Bakiyen: {user['balance']} 💰")

async def maden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    gain = random.randint(100, 1000)
    user["balance"] += gain
    save_db(user_data)
    await update.message.reply_text(f"⛏ Madenden {gain} 💰 kazandin!")

# --- ANA CALISTIRICI ---
if __name__ == '__main__':
    # 1. Web sunucusunu arka planda baslat (Render'ı kandırmak için)
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # 2. Telegram Botu baslat
    print("Bot baslatiliyor...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cuzdan", cuzdan))
    app.add_handler(CommandHandler("maden", maden))
    
    app.run_polling()
