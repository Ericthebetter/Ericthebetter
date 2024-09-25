
import telebot
import os
import zipfile
from telebot import types

# Token do bot
TOKEN = '7376171989:AAG_SIWozis-yYUoQ0nTYFuALgdHWJJ1uKM'
bot = telebot.TeleBot(TOKEN)

# ID autorizado
AUTHORIZED_ID = 6572589301

# Pasta onde os arquivos .py e .zip serão armazenados
FILE_DIRECTORY = './'

# Arquivos a serem ignorados
IGNORED_FILES = {'bot.py', 'loop.py', '.pythonstartup.py', 'za.py'}

# Variável para rastrear se o bot está em modo de aguardando mensagem
awaiting_message = False
current_file = ""

@bot.message_handler(commands=['start'])
def start_message(message):
    if message.from_user.id == AUTHORIZED_ID:
        bot.send_message(message.chat.id, "Bem-vindo ao bot monitorador de arquivos")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id == AUTHORIZED_ID:
        if not awaiting_message:  # Verifica se não está aguardando mensagem
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name

            if file_name.endswith('.py'):
                downloaded_file = bot.download_file(file_info.file_path)
                with open(os.path.join(FILE_DIRECTORY, file_name), 'wb') as new_file:
                    new_file.write(downloaded_file)
                bot.send_message(message.chat.id, f"Arquivo {file_name} recebido com sucesso.")

            elif file_name.endswith('.zip'):
                downloaded_file = bot.download_file(file_info.file_path)
                zip_path = os.path.join(FILE_DIRECTORY, file_name)

                with open(zip_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Extraindo arquivos do .zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(FILE_DIRECTORY)

                bot.send_message(message.chat.id, f"Arquivo {file_name} recebido e extraído com sucesso.")
                
                # Opcional: Remover o arquivo zip após a extração
                os.remove(zip_path)

            else:
                bot.send_message(message.chat.id, "Apenas arquivos .py ou .zip são aceitos.")

@bot.message_handler(commands=['py'])
def list_files(message):
    if message.from_user.id == AUTHORIZED_ID:
        if not awaiting_message:  # Verifica se não está aguardando mensagem
            files = [f for f in os.listdir(FILE_DIRECTORY) if f.endswith('.py') and f not in IGNORED_FILES]
            
            if files:
                markup = types.InlineKeyboardMarkup()
                for file in files:
                    markup.add(types.InlineKeyboardButton(file, callback_data=file))
                bot.send_message(message.chat.id, "Aqui estão todos os seus arquivos:", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Você não tem arquivos .py.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global awaiting_message, current_file  # Usando variáveis globais

    if call.from_user.id == AUTHORIZED_ID:
        if call.data.startswith("confirm_"):
            file_name = call.data.split("_", 1)[1]
            try:
                os.remove(os.path.join(FILE_DIRECTORY, file_name))
                bot.edit_message_text(f"O arquivo {file_name} foi excluído.", chat_id=call.message.chat.id, message_id=call.message.message_id)
            except FileNotFoundError:
                bot.edit_message_text(f"O arquivo já não existe mais no diretório!", chat_id=call.message.chat.id, message_id=call.message.message_id)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"Erro ao excluir o arquivo: {str(e)}")

        elif call.data == "back":
            files = [f for f in os.listdir(FILE_DIRECTORY) if f.endswith('.py') and f not in IGNORED_FILES]
            if files:
                markup = types.InlineKeyboardMarkup()
                for file in files:
                    markup.add(types.InlineKeyboardButton(file, callback_data=file))
                bot.edit_message_text("Aqui estão todos os seus arquivos:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text("Você não tem arquivos .py.", chat_id=call.message.chat.id, message_id=call.message.message_id)

        else:
            file_name = call.data
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Excluir", callback_data=f"excluir_{file_name}"))
            markup.add(types.InlineKeyboardButton("Baixar", callback_data=f"download_{file_name}"))
            markup.add(types.InlineKeyboardButton("Editar", callback_data=f"edit_{file_name}"))
            markup.add(types.InlineKeyboardButton("Voltar", callback_data="back"))
            bot.edit_message_text(f"Você quer excluir o arquivo {file_name}?", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

        # Lógica para o botão de exclusão
        if call.data.startswith("excluir_"):
            file_name = call.data.split("_", 1)[1]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Confirmar", callback_data=f"confirm_{file_name}"))
            markup.add(types.InlineKeyboardButton("Voltar", callback_data="back"))
            bot.edit_message_text(f"Você deseja excluir o arquivo {file_name}?", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

        # Lógica para baixar o arquivo
        if call.data.startswith("download_"):
            file_name = call.data.split("_", 1)[1]
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                
                with open(os.path.join(FILE_DIRECTORY, file_name), 'rb') as file:
                    bot.send_document(AUTHORIZED_ID, file, caption=f"Aqui está o arquivo {file_name}.")
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, f"O arquivo já não existe mais no diretório!")

        # Lógica para editar o arquivo
        if call.data.startswith("edit_"):
            current_file = call.data.split("_", 1)[1]
            awaiting_message = True
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, f"Envie o conteúdo que deseja adicionar no arquivo {current_file}.")

@bot.message_handler(func=lambda message: awaiting_message, content_types=['text'])
def handle_edit(message):
    global awaiting_message, current_file

    # Remove qualquer comando ou mensagem não textual
    if message.from_user.id == AUTHORIZED_ID:
        with open(os.path.join(FILE_DIRECTORY, current_file), 'w') as file:
            file.write(message.text)  # Sobrescrevendo o arquivo com o novo conteúdo
        bot.send_message(message.chat.id, f"O arquivo {current_file} foi atualizado com sucesso.")
        awaiting_message = False  # Sai do modo de aguardando mensagem
        current_file = ""  # Limpa a variável do arquivo atual

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_unexpected_messages(message):
    # Se não está em modo de aguardando mensagem, ignora
    if not awaiting_message and message.from_user.id == AUTHORIZED_ID:
        bot.delete_message(message.chat.id, message.message_id)  # Apaga qualquer mensagem não permitida

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}. Reiniciando o bot...")
            time.sleep(0)  # Aguarda 0 segundos antes de reiniciar

# Chame a função para iniciar o bot
run_bot()
