import os
import random
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- AYARLAR ---
TOKEN = '8071326897:AAF5tqcTz7SxDulJ8nskD6rftIoqvQ46mZo' 
GOD_IDS = [8696460554] # Kendi Telegram ID'ni yaz
DB_FILE = "database.json"

# --- RENDER İÇİN WEB SUNUCUSU (Kapanmaması İçin Şart) ---
def run_web_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Aktif ve Calisiyor!")
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# --- VERİTABANI İŞLEMLERİ ---
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
        user_data[uid] = {"balance": 1000, "last_mine": 0, "last_fish": 0}
    return user_data[uid]

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎮 **Ekonomi Botu Aktif!**\n\n/cuzdan - Bakiyeni gör\n/maden - Para kazan (15dk)\n/slot <miktar> - Şansını dene\n/zar <miktar> - Zar at\n/transfer <miktar> - (Yanıtlayarak) Para gönder"
    await update.message.reply_text(text, parse_mode="Markdown")

async def cuzdan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Mevcut Bakiyen: {user['balance']} 💰")

async def maden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    now = time.time()
    if now - user.get("last_mine", 0) < 900: # 15 dakika
        kalan = 900 - (now - user["last_mine"])
        return await update.message.reply_text(f"⏳ Dinlenmelisin! Kalan: {int(kalan/60)} dk.")
    
    gain = random.randint(200, 2000)
    user["balance"] += gain
    user["last_mine"] = now
    save_db(user_data)
    await update.message.reply_text(f"⛏ Madenden {gain} 💰 kazandın! \nGüncel: {user['balance']} 💰")

async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    try:
        bet = int(context.args[0])
    except: return await update.message.reply_text("Kullanım: /slot <miktar>")
    
    if bet > user["balance"] or bet <= 0:
        return await update.message.reply_text("❌ Yetersiz bakiye!")

    emojis = ["🍎", "💎", "🎰", "🔔", "🍒"]
    res = [random.choice(emojis) for _ in range(3)]
    slot_res = f"🎰 [ {' | '.join(res)} ]"
    
    if res[0] == res[1] == res[2]:
        win = bet * 10
        user["balance"] += win
        msg = f"{slot_res}\n🔥 JACKPOT! 10 KATINI KAZANDIN: {win} 💰"
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
        win = int(bet * 1.5)
        user["balance"] += win
        msg = f"{slot_res}\n✅ Güzel! 1.5 katı kazandın: {win} 💰"
    else:
        user["balance"] -= bet
        msg = f"{slot_res}\n💸 Kaybettin! {bet} 💰 gitti."
    
    save_db(user_data)
    await update.message.reply_text(msg)

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = get_user(update.effective_user.id)
    if not update.message.reply_to_message:
        return await update.message.reply_text("Para göndermek için birinin mesajını yanıtla!")
    try:
        amount = int(context.args[0])
        if amount > sender["balance"] or amount <= 0:
            return await update.message.reply_text("❌ Yetersiz bakiye!")
        
        target_id = str(update.message.reply_to_message.from_user.id)
        receiver = get_user(target_id)
        sender["balance"] -= amount
        receiver["balance"] += amount
        save_db(user_data)
        await update.message.reply_text(f"✅ {amount} 💰 başarıyla gönderildi!")
    except: await update.message.reply_text("Kullanım: /transfer <miktar>")

async def give_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in GOD_IDS: return
    try:
        amount = int(context.args[0])
        target_id = str(update.message.reply_to_message.from_user.id) if update.message.reply_to_message else str(context.args[1])
        get_user(target_id)["balance"] += amount
        save_db(user_data)
        await update.message.reply_text(f"⚡ Admin: {amount} 💰 eklendi.")
    except: await update.message.reply_text("Kullanım: /ver <miktar>")

# --- ANA PROGRAM ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cuzdan", cuzdan))
    app.add_handler(CommandHandler("maden", maden))
    app.add_handler(CommandHandler("slot", slot))
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("ver", give_money))

    print("Bot tüm fonksiyonlarla başlatıldı...")
    app.run_polling()
      
