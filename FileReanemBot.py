from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
import threading, os

TOKEN = os.environ.get("8772139464:AAEfHsIn8uqI39HZM-BuOR6h-G9JS_YQJj0")  # Render Secret

user_files = {}
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Welcome to Public Rename Bot!\nSend me a file/video to rename.")

def handle_file(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    file = update.message.document or update.message.video
    if not file:
        update.message.reply_text("❌ Send a valid file/video.")
        return
    user_files[chat_id] = file.file_id
    update.message.reply_text("✏️ Send new file name with extension:")

def rename_file(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if chat_id not in user_files:
        return
    new_name = update.message.text.strip()
    file_id = user_files[chat_id]
    f = context.bot.get_file(file_id)
    path = f"/tmp/{new_name}"
    f.download(path)
    with open(path, "rb") as file:
        context.bot.send_document(chat_id, file, caption="✅ File renamed!")
    os.remove(path)
    del user_files[chat_id]

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document | Filters.video, handle_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, rename_file))
    updater.start_polling()
    updater.idle()

# Flask server to keep alive
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

run_bot()
