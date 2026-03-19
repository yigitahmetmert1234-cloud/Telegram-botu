import logging
import random
import json
import os
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters

# --- AYARLAR ---
TOKEN = '8071326897:AAF5tqcTz7SxDulJ8nskD6rftIoqvQ46mZo'
GOD_IDS = [8696460554],[1569703107],[8692958120]  # Kendi Telegram ID'ni buraya yaz (Sınırsız para basma yetkisi)
DB_FILE = "database.json"

# --- VERİTABANI İŞLEMLERİ ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_db()

def get_user(user_id):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {
            "balance": 1000, 
            "last_mine": 0, 
            "last_fish": 0
        }
    return user_data[uid]

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

# --- KOMUTLAR ---

# 1. Start / Yardım Menüsü
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🎮 **Gelişmiş Ekonomi Botu Menüsü**

💰 **Cüzdan İşlemleri:**
/cuzdan - Bakiyeni gör
/transfer <miktar> - (Bir mesaja yanıt vererek) Para gönder
/daily - Günlük ödül (Her gün 1 kez)

🎲 **Şans Oyunları:**
/slot <miktar> - Slot çevir (Eşleşmeye göre kazan)
/zar <miktar> - Botla zar düellosu yap

⚒ **Bedava Para Kazanma:**
/maden - 15 dk'da bir maden kaz (100-3000 💰)
/balik - 10 dk'da bir balık tut (100-3000 💰)

⚡ **God Mode (Admin):**
/ver <miktar> - (Yanıtlayarak veya ID ile) Para basar.
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

# 2. Maden Kazma (15 Dakika Cooldown)
async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    now = time.time()
    wait_time = 15 * 60

    if now - user.get("last_mine", 0) < wait_time:
        remaining = wait_time - (now - user["last_mine"])
        return await update.message.reply_text(f"⚒ Dinlenmelisin! Kalan süre: {format_time(remaining)}")

    gain = random.randint(100, 3000)
    user["balance"] += gain
    user["last_mine"] = now
    save_db(user_data)
    await update.message.reply_text(f"⛏ Madenden {gain} 💰 çıkardın! \nGüncel: {user['balance']} 💰")

# 3. Balık Tutma (10 Dakika Cooldown)
async def fish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = get_user(uid)
    now = time.time()
    wait_time = 10 * 60

    if now - user.get("last_fish", 0) < wait_time:
        remaining = wait_time - (now - user["last_fish"])
        return await update.message.reply_text(f"🎣 Balıklar kaçtı! Kalan süre: {format_time(remaining)}")

    gain = random.randint(100, 3000)
    user["balance"] += gain
                
