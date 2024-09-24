import telebot
from telebot import types
import requests
import os

# Configurações do bot
API_TOKEN = '7494930693:AAHvowJiyxbbXvUJpuD5I7A65DpLI59zJxE'
bot = telebot.TeleBot(API_TOKEN)

URL = "https://chatbot-ji1z.onrender.com/chatbot-ji1z"
headers = {
    "Host": "chatbot-ji1z.onrender.com",
    "content-length": "57",
    "sec-ch-ua": "\"Chromium\";v\u003d\"124\", \"Android WebView\";v\u003d\"124\", \"Not-A.Brand\";v\u003d\"99\"",
    "accept": "application/json",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?1",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; SM-J400M Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.123 Mobile Safari/537.36",
    "sec-ch-ua-platform": "\"Android\"",
    "origin": "https://seoschmiede.at",
    "x-requested-with": "mark.via.gp",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "cookie": "pt-BR,pt;q\u003d0.9,en-US;q\u003d0.8,en;q\u003d0.7",
    "priority": "u\u003d1, i"
}

historico = {}

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

@bot.message_handler(commands=['start'])
def start_message(message):
    id = message.from_user.id
    nome = message.from_user.first_name

    if id not in historico:
        historico[id] = []
        bot.send_message(message.chat.id, f"""Olá {nome}!

Seja bem-vindo ao nosso assistente de inteligência artificial!

**desenvolvedores:**
- @ericfelipeP
- @ericfelipeS

... (mensagem continua) ...

Atenciosamente, Desenvolvedores 👋""", reply_markup=get_start_keyboard())
    else:
        bot.send_message(message.chat.id, "Para acessar a mensagem /start é necessário fechar o diálogo primeiro", reply_markup=get_action_keyboard())

@bot.message_handler(commands=['reset'])
def reset_message(message):
    id = message.from_user.id
    historico[id] = []
    bot.send_message(message.chat.id, "Histórico reiniciado com sucesso!")

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    id = message.from_user.id
    b2 = message.text

    if message.from_user.is_bot:
        return

    # Verificar e criar o diretório
    dir_path = '/storage/emulated/0/conversa'
    ensure_directory_exists(dir_path)

    file_path = f"{dir_path}/{message.from_user.username}.txt"
    with open(file_path, "a") as file:
        if file.tell() == 0:
            file.write("informações do usuário.")
            file.write(f"ID: {id}\n")
            file.write(f"Username: {message.from_user.username}\nnome: {message.from_user.first_name}ㅤ\nㅤ\nㅤ\nㅤ\nㅤ")
            file.write("diálogo abaixo!")
        
        file.write(f"\n{message.from_user.username}:{b2}\n")

    if id in historico:
        historico[id].append({"role": "user", "content": b2})
        projection_message = bot.send_message(message.chat.id, "Projetando a resposta...")
        
        data = {"messages": historico[id]} 
        s = requests.post(URL, headers=headers, json=data)
        S2 = s.json()
        S3 = S2['choices'][0]['message']['content']

        with open(file_path, "a") as file:
            file.write(f"-\nBot: {S3}\n")

        historico[id].append({"role": "assistant", "content": S3})
        
        bot.edit_message_text(S3, chat_id=message.chat.id, message_id=projection_message.message_id)
    else:
        bot.send_message(message.chat.id, "Clique no botão iniciar pra começar a interação.", reply_markup=get_start_keyboard())

def get_start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Iniciar", callback_data="start"))
    return keyboard

def get_action_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Parar", callback_data="parar"))
    return keyboard

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global historico
    id = call.from_user.id
    action = call.data

    if action == "start":
        if id not in historico:
            historico[id] = []
            historico[id].append({"role": "user", "content": "/iniciar"})
            bot.edit_message_text("Interação iniciada! Em que posso ajudar?", chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.edit_message_text(f"Já existe um diálogo aberto {call.from_user.first_name}!", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif action == "parar":
        if id in historico:
            historico[id] = []
            del historico[id]
            bot.edit_message_text("Diálogo encerrado.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            bot.edit_message_text(f"Não há um diálogo aberto para ser encerrado {call.from_user.first_name}.", chat_id=call.message.chat.id, message_id=call.message.message_id)

bot.polling()
