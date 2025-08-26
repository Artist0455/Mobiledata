import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

# --- Database setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, mobile TEXT)")
conn.commit()

# --- Telegram Bot Functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Contact Bot!\n\n"
        "📌 Commands:\n"
        "➕ /add <username> <mobile>\n"
        "🔍 /find <username>\n"
        "❌ /delete <username>\n\n"
        "💡 Or just type a username directly to search."
    )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <username> <mobile>")
        return
    username, mobile = context.args
    cursor.execute("INSERT INTO users VALUES (?, ?)", (username, mobile))
    conn.commit()
    await update.message.reply_text(f"✅ Added {username} → {mobile}")

async def find_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /find <username>")
        return
    username = context.args[0]
    cursor.execute("SELECT mobile FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(f"📱 {username} → {result[0]}")
    else:
        await update.message.reply_text("❌ Not found in database.")

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /delete <username>")
        return
    username = context.args[0]
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    if cursor.rowcount > 0:
        await update.message.reply_text(f"🗑️ Deleted {username}.")
    else:
        await update.message.reply_text("❌ Username not found.")

async def search_by_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    cursor.execute("SELECT mobile FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(f"📱 {username} → {result[0]}")
    else:
        await update.message.reply_text("❌ Not found. Use /add to save it.")

# --- Telegram Bot Setup ---
TOKEN = os.getenv("8479080326:AAG_ltoHfV21q1vGa5u4T-gLmL6BzfwKLDQ")  # Safe from Render Environment Variable
app_bot = Application.builder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("add", add_user))
app_bot.add_handler(CommandHandler("find", find_user))
app_bot.add_handler(CommandHandler("delete", delete_user))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_username))

def run_bot():
    print("🤖 Bot running...")
    app_bot.run_polling()

# --- Flask Web Server ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

if __name__ == "__main__":
    # Run Telegram bot in separate thread
    threading.Thread(target=run_bot).start()
    # Run Flask server (Render needs this)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    
