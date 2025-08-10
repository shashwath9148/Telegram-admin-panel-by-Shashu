import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN") 
ADMIN_TELEGRAM_ID = int(os.getenv('1046270147', '0'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
DB = "bot.db"

def add_or_update_user(telegram_user):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
      INSERT OR IGNORE INTO users(telegram_id, username, first_name, last_name)
      VALUES(?,?,?,?)
    ''', (telegram_user.id, telegram_user.username, telegram_user.first_name, telegram_user.last_name))
    c.execute('''
      UPDATE users SET username=?, first_name=?, last_name=?
      WHERE telegram_id=?
    ''', (telegram_user.username, telegram_user.first_name, telegram_user.last_name, telegram_user.id))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user)
    conn = sqlite3.connect(DB)
    banned = conn.execute('SELECT banned FROM users WHERE telegram_id=?', (user.id,)).fetchone()[0]
    conn.close()
    if banned:
        await update.message.reply_text("You are banned from using this bot.")
        return
    await update.message.reply_text(f"Hello {user.first_name}! This is the bot. Use /help to see commands.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/start - register\n"
        "/help - this help\n"
        "/me - show your info\n"
        "Admin-only: /stats, /users, /ban <tg_id>, /unban <tg_id>, /broadcast <message>"
    )
    await update.message.reply_text(text)

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text(f"ID: {u.id}\nUsername: @{u.username}\nName: {u.first_name} {u.last_name or ''}")

def is_admin(telegram_id):
    return telegram_id == ADMIN_TELEGRAM_ID

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("Unauthorized.")
        return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    total = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    banned = c.execute('SELECT COUNT(*) FROM users WHERE banned=1').fetchone()[0]
    premium = c.execute('SELECT COUNT(*) FROM users WHERE is_premium=1').fetchone()[0]
    conn.close()
    await update.message.reply_text(f"Users: {total}\nBanned: {banned}\nPremium: {premium}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("Unauthorized.")
        return
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT telegram_id, username, first_name, banned FROM users ORDER BY created_at DESC LIMIT 200').fetchall()
    conn.close()
    text = "Recent users:\n" + "\n".join([f"{r[0]} | @{r[1] or '-'} | {r[2] or '-'} | banned={r[3]}" for r in rows])
    await update.message.reply_text(text[:4000])

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <telegram_id>")
        return
    target = context.args[0]
    conn = sqlite3.connect(DB)
    conn.execute('UPDATE users SET banned=1 WHERE telegram_id=?', (target,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"Banned {target}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <telegram_id>")
        return
    target = context.args[0]
    conn = sqlite3.connect(DB)
    conn.execute('UPDATE users SET banned=0 WHERE telegram_id=?', (target,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"Unbanned {target}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("Unauthorized.")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT telegram_id FROM users WHERE banned=0').fetchall()
    conn.close()
    sent = 0
    app = context.application
    for (tgid,) in rows:
        try:
            await app.bot.send_message(chat_id=int(tgid), text=text)
            sent += 1
        except Exception as e:
            logging.warning(f"Failed to send to {tgid}: {e}")
    await update.message.reply_text(f"Broadcast sent to {sent} users.")

async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_or_update_user(user)
    if update.message.text:
        await update.message.reply_text("Message received. Use /help for commands.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), any_message))
    print("Bot started (polling).")
    app.run_polling()

if __name__ == "__main__":
    main()
