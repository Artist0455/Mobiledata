import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Database setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, mobile TEXT)")
conn.commit()

# --- Add user function ---
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <username> <mobile>")
        return
    username, mobile = context.args
    cursor.execute("INSERT INTO users VALUES (?, ?)", (username, mobile))
    conn.commit()
    await update.message.reply_text(f"✅ Added {username} → {mobile}")

# --- Find user function ---
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

# --- Main ---
TOKEN = "8479080326:AAG_ltoHfV21q1vGa5u4T-gLmL6BzfwKLDQ"

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("add", add_user))
app.add_handler(CommandHandler("find", find_user))

print("🤖 Bot running...")
app.run_polling()
