import telebot
import time
import threading

# Substitua pelo seu token
TOKEN = '7320479686:AAGitIDu66u-QHuatQzyYfpYo8fzkCxKz_Y'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Envie /meuid pra saber seu id", parse_mode='MarkdownV2')

@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"*Seu ID é*: `{user_id}`", parse_mode='MarkdownV2')

def keep_alive():
    while True:
        print("Mantendo a sessão ativa...")
        time.sleep(600)  # Aguarda 10 minutos

# Inicia a thread para manter a sessão ativa
threading.Thread(target=keep_alive).start()

# Inicia o bot
bot.polling()
