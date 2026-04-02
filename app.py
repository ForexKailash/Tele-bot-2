from flask import Flask, request
import telebot
import os

# --- Bot Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- Webhook Route ---
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Bad Request', 400

# --- Test Route ---
@app.route('/')
def hello():
    return "Telegram Bot is running!"

# --- Set Webhook on Startup ---
def set_webhook():
    """Sets the webhook for the bot on startup."""
    try:
        bot.remove_webhook()
        webhook_url = f"{WEBHOOK_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set successfully to {webhook_url}")
    except Exception as e:
        print(f"Failed to set webhook: {e}")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)
