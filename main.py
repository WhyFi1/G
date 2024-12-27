import telebot
from cryptography.fernet import Fernet
import base64

# Replace with your bot token from BotFather
BOT_TOKEN = "7975337048:AAEYFx_UyG8NPlgT3ed9fnoBs0Y-ObO9UoU"

bot = telebot.TeleBot(BOT_TOKEN)

# Generate a key for AES encryption (use this key for Fernet encryption)
fernet_key = Fernet.generate_key()
cipher_suite = Fernet(fernet_key)

# State management for user interaction
user_state = {}


def reset_user_state(user_id):
    """Reset the user's state to clear any pending actions."""
    if user_id in user_state:
        del user_state[user_id]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    reset_user_state(message.chat.id)
    bot.reply_to(
        message,
        "Welcome to the Encryption Bot!\n"
        "You can encrypt or decrypt any code or text.\n\n"
        "Commands:\n"
        "/encrypt - Encrypt your text (choose method later)\n"
        "/decrypt - Decrypt your text (choose method later)\n"
        "/reset - Reset current operation"
    )


@bot.message_handler(commands=['reset'])
def reset_command(message):
    reset_user_state(message.chat.id)
    bot.reply_to(message, "Your operation has been reset. Start again!")


@bot.message_handler(commands=['encrypt'])
def encrypt_command(message):
    user_state[message.chat.id] = {'action': 'encrypt'}
    bot.reply_to(message, "Send the text you want to encrypt:")


@bot.message_handler(commands=['decrypt'])
def decrypt_command(message):
    user_state[message.chat.id] = {'action': 'decrypt'}
    bot.reply_to(message, "Send the text you want to decrypt:")


@bot.message_handler(func=lambda message: message.chat.id in user_state)
def handle_text(message):
    user_id = message.chat.id
    if 'action' in user_state[user_id]:
        action = user_state[user_id]['action']

        if action == 'encrypt':
            user_state[user_id]['text'] = message.text
            bot.reply_to(
                message,
                "Choose an encryption method:\n"
                "1. Base64 (reply with 'base64')\n"
                "2. AES (reply with 'aes')"
            )

        elif action == 'decrypt':
            user_state[user_id]['text'] = message.text
            bot.reply_to(
                message,
                "Choose a decryption method:\n"
                "1. Base64 (reply with 'base64')\n"
                "2. AES (reply with 'aes')"
            )

    elif 'method' in user_state[user_id]:
        handle_encryption_decryption(message)


def handle_encryption_decryption(message):
    user_id = message.chat.id
    method = message.text.lower()
    user_text = user_state[user_id]['text']
    action = user_state[user_id]['action']

    try:
        if action == 'encrypt':
            if method == 'base64':
                result = base64.b64encode(user_text.encode()).decode()
                bot.reply_to(message, f"Base64 Encrypted:\n{result}")
            elif method == 'aes':
                result = cipher_suite.encrypt(user_text.encode()).decode()
                bot.reply_to(message, f"AES Encrypted:\n{result}")
            else:
                bot.reply_to(message, "Invalid method. Please reply with 'base64' or 'aes'.")

        elif action == 'decrypt':
            if method == 'base64':
                result = base64.b64decode(user_text.encode()).decode()
                bot.reply_to(message, f"Base64 Decrypted:\n{result}")
            elif method == 'aes':
                result = cipher_suite.decrypt(user_text.encode()).decode()
                bot.reply_to(message, f"AES Decrypted:\n{result}")
            else:
                bot.reply_to(message, "Invalid method. Please reply with 'base64' or 'aes'.")
        else:
            bot.reply_to(message, "Unknown action. Use /encrypt or /decrypt to start.")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

    # Reset user state after completion
    reset_user_state(user_id)


# Start the bot
print("Bot is running...")
bot.polling()
