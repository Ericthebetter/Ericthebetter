
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import mercadopago
import qrcode
import io
import asyncio
import threading
import time
import os
import re
from datetime import datetime, timedelta
import random

# Token do bot
API_TOKEN = '7326633330:AAE305xpjWM37i8cfw9YEEA5NZbSGJA1a6c'
bot = telebot.TeleBot(API_TOKEN)

# Configurações do Mercado Pago
credentials = {
    'access_token': 'APP_USR-1966823255324179-081817-d5f29888884a2dba8dfac4e5fbc2e15b-1613838000'
}

# Diretório para armazenar os arquivos de saldo
USER_DATA_DIR = 'iamonitorbot'

# Dicionário para rastrear pedidos Pix pendentes
pending_pix = {}
# Dicionário para rastrear se o bot está aguardando um valor
waiting_for_value = {}

# Lista de aplicativos com valores aleatórios
apps = [
    ("Airbnb", round(random.uniform(0.10, 4.00), 2)),
    ("AliExpress", round(random.uniform(0.10, 4.00), 2)),
    ("Amazon", round(random.uniform(0.10, 4.00), 2)),
    ("Apple ID", round(random.uniform(0.10, 4.00), 2)),
    ("Binance", round(random.uniform(0.10, 4.00), 2)),
    ("Booking.com", round(random.uniform(0.10, 4.00), 2)),
    ("Bumble", round(random.uniform(0.10, 4.00), 2)),
    ("Cash App", round(random.uniform(0.10, 4.00), 2)),
    ("Cashify", round(random.uniform(0.10, 4.00), 2)),
    ("Coinbase", round(random.uniform(0.10, 4.00), 2)),
    ("Coursera", round(random.uniform(0.10, 4.00), 2)),
    ("Discord", round(random.uniform(0.10, 4.00), 2)),
    ("DoorDash", round(random.uniform(0.10, 4.00), 2)),
    ("Dropbox", round(random.uniform(0.10, 4.00), 2)),
    ("eBay", round(random.uniform(0.10, 4.00), 2)),
    ("Etsy", round(random.uniform(0.10, 4.00), 2)),
    ("Eventbrite", round(random.uniform(0.10, 4.00), 2)),
    ("Expedia", round(random.uniform(0.10, 4.00), 2)),
    ("Facebook", round(random.uniform(0.10, 4.00), 2)),
    ("Google", round(random.uniform(0.10, 4.00), 2)),
    ("Grubhub", round(random.uniform(0.10, 4.00), 2)),
    ("Hulu", round(random.uniform(0.10, 4.00), 2)),
    ("Instagram", round(random.uniform(0.10, 4.00), 2)),
    ("Kijiji", round(random.uniform(0.10, 4.00), 2)),
    ("Kwai", round(random.uniform(0.10, 4.00), 2)),
    ("LinkedIn", round(random.uniform(0.10, 4.00), 2)),
    ("Lyft", round(random.uniform(0.10, 4.00), 2)),
    ("Mercado Livre", round(random.uniform(0.10, 4.00), 2)),
    ("Mercado Pago", round(random.uniform(0.10, 4.00), 2)),
    ("Netflix", round(random.uniform(0.10, 4.00), 2)),
    ("Nubank", round(random.uniform(0.10, 4.00), 2)),
    ("OLX", round(random.uniform(0.10, 4.00), 2)),
    ("PayPal", round(random.uniform(0.10, 4.00), 2)),
    ("Pinterest", round(random.uniform(0.10, 4.00), 2)),
    ("Postmates", round(random.uniform(0.10, 4.00), 2)),
    ("Quora", round(random.uniform(0.10, 4.00), 2)),
    ("Reddit", round(random.uniform(0.10, 4.00), 2)),
    ("Robinhood", round(random.uniform(0.10, 4.00), 2)),
    ("Shopify", round(random.uniform(0.10, 4.00), 2)),
    ("Signal", round(random.uniform(0.10, 4.00), 2)),
    ("Slack", round(random.uniform(0.10, 4.00), 2)),
    ("Snapchat", round(random.uniform(0.10, 4.00), 2)),
    ("Spotify", round(random.uniform(0.10, 4.00), 2)),
    ("TikTok", round(random.uniform(0.10, 4.00), 2)),
    ("TripAdvisor", round(random.uniform(0.10, 4.00), 2)),
    ("Twitch", round(random.uniform(0.10, 4.00), 2)),
    ("Uber", round(random.uniform(0.10, 4.00), 2)),
    ("VK", round(random.uniform(0.10, 4.00), 2)),
    ("WhatsApp", 4.20),  # WhatsApp com preço fixo
    ("Telegram", 3.53),  # Telegram com preço fixo
    ("Outros", 2.69),    # Outros com preço fixo
]

def ensure_user_file(user_id):
    """Garante que o arquivo do usuário exista com saldo inicial."""
    user_file_path = os.path.join(USER_DATA_DIR, f"{user_id}.txt")

    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    if not os.path.isfile(user_file_path):
        with open(user_file_path, 'w') as user_file:
            user_file.write("SALDO = 0.00\nREGISTRO = 0\n")
    return user_file_path

def get_user_balance(user_id):
    """Lê o saldo do usuário a partir do arquivo."""
    user_file_path = ensure_user_file(user_id)

    with open(user_file_path, 'r') as user_file:
        lines = user_file.readlines()
        for line in lines:
            if line.startswith("SALDO ="):
                return float(line.split('=')[1].strip())
    return 0.00

def update_user_balance(user_id, amount):
    """Atualiza o saldo do usuário no arquivo."""
    user_file_path = ensure_user_file(user_id)
    current_balance = get_user_balance(user_id)
    new_balance = current_balance + amount

    with open(user_file_path, 'w') as user_file:
        user_file.write(f"SALDO = {new_balance:.2f}\nREGISTRO = 0\n")
    return new_balance

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    # Exclui a mensagem original do usuário
    bot.delete_message(message.chat.id, message.message_id)
    namer = message.from_user.first_name

    # Mensagem de boas-vindas
    welcome_message = (
        f"👋 *Bem-vindo {namer}*, é um prazer tê-lo aqui! \n\n"
        f"*SEU SALDO É:* *{balance:.2f} BRL*\n\n"
        "*BEM-VINDO AO NOSSO SISTEMA!* 📨\n\n"
        "*DESCUBRA NOSSOS SERVIÇOS E AFILIADOS AQUI EMBAIXO!* 💼"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🛠️ SERVIÇOS", callback_data="servicos"))
    keyboard.add(InlineKeyboardButton("💳 RECARREGAR", callback_data="select_payment"))
    keyboard.add(InlineKeyboardButton("🔗 AFILIADO", callback_data="afiliado"))

    # Envia a mensagem de boas-vindas
    bot.send_message(message.chat.id, escape_markdown_v2(welcome_message), reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == "servicos")
def servicos_command(call):
    user_id = call.from_user.id
    saldo = get_user_balance(user_id)

    buttons = []
    # Adiciona os serviços de Airbnb até Venmo em duas colunas
    for i in range(0, len(apps) - 3, 2):  # Exclui os últimos 3 (WhatsApp, Telegram, Outros)
        button1_text = f"{apps[i][0]} | R$ {apps[i][1]:.2f}"
        button2_text = f"{apps[i + 1][0]} | R$ {apps[i + 1][1]:.2f}" if i + 1 < len(apps) - 3 else ""

        row = []
        row.append(InlineKeyboardButton(button1_text, callback_data=f"app_{apps[i][0]}"))
        if button2_text:
            row.append(InlineKeyboardButton(button2_text, callback_data=f"app_{apps[i + 1][0]}"))
        buttons.append(row)

    # Adiciona o botão de recarregar
    buttons.append([InlineKeyboardButton("💳 Recarregar", callback_data="select_payment")])

    # Adiciona os serviços fixos na vertical
    buttons.append([InlineKeyboardButton("WhatsApp | R$ 4.20", callback_data="app_WhatsApp")])
    buttons.append([InlineKeyboardButton("Telegram | R$ 3.53", callback_data="app_Telegram")])
    buttons.append([InlineKeyboardButton("Outros | R$ 2.69", callback_data="app_Outros")])

    buttons.append([InlineKeyboardButton("🏠 MENU INICIAL", callback_data="menu_inicial")])

    servicos_message = f"💰 *SEU SALDO:* *{saldo:.2f} BRL*"
    bot.edit_message_text(escape_markdown_v2(servicos_message), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def app_selected(call):
    user_id = call.from_user.id  # Obtenha o user_id a partir do objeto call
    balance = get_user_balance(user_id)  # Use o user_id correto

    if balance == 0.00:
        bot.answer_callback_query(call.id, "Saldo insuficiente ⚠️", show_alert=True)
        return

    bot.answer_callback_query(call.id, "Estamos em manutenção 🛠️", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "afiliado")
def afiliado_command(call):
    user_id = call.from_user.id
    link = f"https://t.me/numerosvirtuaisfree_Bot?start={user_id}"

    affiliate_message = (
        "1. *Quando um usuário entrar pelo seu link e realizar uma recarga, você receberá 15% de bônus referente ao valor depositado!* 💰\n\n"
        "2. *Se você convidar 20 pessoas e elas clicarem no seu link para entrar no Bot, você terá o direito de escolher qualquer serviço da lista!* 📋\n\n"
        "*Essas 20 pessoas não precisam realizar recarga para que você ganhe a recompensa.* 🤝\n\n"
        "*Essa recompensa é dada para incentivar as pessoas a compartilhar o Bot e atrair mais clientes para o nosso serviço.* 🚀\n\n"
        "*O máximo de convites dessa promoção permitidos é de 40 pessoas resultando na escolha de até 2 serviços!* 📈\n\n"
        "*Recompensas de recargas não têm limite de usuário. Então divulgue o máximo pra obter várias recompensas!* 💸\n\n"
        "📌 *APROVEITE ESSA OPORTUNIDADE!*\n\n"
        "*CLIQUE EM CIMA PARA COPIAR O SEU LINK ABAIXO E JÁ COMECE A DIVULGAR!*\n\n"
        f"🔗:`{link}`"
    )

    buttons = [
        [InlineKeyboardButton("🏠 MENU INICIAL", callback_data="menu_inicial")]
    ]

    bot.edit_message_text(escape_markdown_v2(affiliate_message), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == "menu_inicial")
def menu_inicial_command(call):
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    welcome_message = (
        f"👋 *Olá novamente!* É um prazer tê-lo aqui! \n\n"
        f"*SEU SALDO É:* *{balance:.2f} BRL*\n\n"
        "*BEM-VINDO AO NOSSO SISTEMA!* 📨\n\n"
        "*DESCUBRA NOSSOS SERVIÇOS E AFILIADOS AQUI EMBAIXO!* 💼"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🛠️ SERVIÇOS", callback_data="servicos"))
    keyboard.add(InlineKeyboardButton("💳 RECARREGAR", callback_data="select_payment"))
    keyboard.add(InlineKeyboardButton("🔗 AFILIADO", callback_data="afiliado"))

    bot.edit_message_text(escape_markdown_v2(welcome_message), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == "select_payment")
def select_payment_method(call):
    user_id = call.from_user.id
    if pending_pix.get(user_id):
        bot.answer_callback_query(call.id, "Você tem uma ordem em andamento", show_alert=True)
    else:
        waiting_for_value[user_id] = False
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💳 Pix", callback_data="pay_pix"))
        keyboard.add(InlineKeyboardButton("🔙 Voltar", callback_data="back_to_start"))
        bot.edit_message_text(escape_markdown_v2("SELECIONE O MEIO DE PAGAMENTO 💳"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start(call):
    user_id = call.from_user.id
    balance = get_user_balance(user_id)
    response_message = escape_markdown_v2(f"👋 *Olá novamente 😁*, é um prazer tê-lo aqui! \n\n"         f"*SEU SALDO É:* *{balance:.2f} BRL*\n\n"         "*BEM-VINDO AO NOSSO SISTEMA!* 📨\n\n"         "*DESCUBRA NOSSOS SERVIÇOS E AFILIADOS AQUI EMBAIXO!* 💼")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🛠️ SERVIÇOS", callback_data="servicos"))
    keyboard.add(InlineKeyboardButton("💳 RECARREGAR", callback_data="select_payment"))
    keyboard.add(InlineKeyboardButton("🔗 AFILIADO", callback_data="afiliado"))

    bot.edit_message_text(response_message, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: call.data == "pay_pix")
def request_pix_amount(call):
    user_id = call.from_user.id
    if pending_pix.get(user_id):
        bot.answer_callback_query(call.id, "Você tem uma ordem em andamento", show_alert=True)
    else:
        waiting_for_value[user_id] = True
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 Voltar", callback_data="select_payment"))  # Volta para "Selecione o meio de pagamento"
        bot.edit_message_text(escape_markdown_v2("ENVIE O VALOR QUE DESEJA RECARREGAR (MÍNIMO 10, MÁXIMO 5000)"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.register_next_step_handler(call.message, process_recharge_amount, call.message.message_id)

def process_recharge_amount(message, original_message_id):
    user_id = message.from_user.id
    if not waiting_for_value.get(user_id, False):
        return  # Se não está esperando um valor, não faz nada

    try:
        amount_str = message.text.replace(',', '.')
        # Verifica se é um número válido antes de tentar converter para float
        if re.match(r'^\d+(\.\d{1,2})?$', amount_str):
            amount = float(amount_str)
            if 10 <= amount <= 5000:
                # Enviar mensagem de geração de Pix
                processing_message = bot.send_message(message.chat.id, f"Gerando Pix de {amount:.2f}...")
                bot.delete_message(message.chat.id, original_message_id)
                send_pix_payment(message, amount, processing_message)  # Passa a mensagem de processamento
                return

        # Se não for um valor válido, apaga a mensagem do usuário
        bot.delete_message(message.chat.id, message.message_id)
        error_message = bot.send_message(message.chat.id, "Valor inválido ❌")
        threading.Timer(2.0, lambda: bot.delete_message(message.chat.id, error_message.message_id)).start()
    except ValueError:
        # Se não puder ser convertido para float, apaga a mensagem do usuário e envia mensagem de erro
        bot.delete_message(message.chat.id, message.message_id)
        error_message = bot.send_message(message.chat.id, "Entrada inválida. Por favor, envie um valor numérico.")
        threading.Timer(2.0, lambda: bot.delete_message(message.chat.id, error_message.message_id)).start()

    # Rechama a função para tentar novamente
    request_pix_amount_next(message, original_message_id)

def request_pix_amount_next(message, original_message_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Voltar", callback_data="select_payment"))  # Ajustado para voltar corretamente

    # Aqui, não editamos a mensagem se ela já está correta, apenas aguardamos a próxima entrada
    bot.register_next_step_handler(message, process_recharge_amount, original_message_id)

def send_pix_payment(message, amount, processing_message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Usuário"
    cpf = "00000000000"  # Substitua pelo CPF real do usuário

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        qr_code_data, payment_id = loop.run_until_complete(generate_payment(amount, user_name, cpf))
        qr_image = generate_qr_code(qr_code_data)

        expiration_time = datetime.now() + timedelta(seconds=1800)

        details_message = (
            f"*PIX GERADO!*\n\n"
            f"*VALOR À PAGAR:* *{amount:.2f} BRL* 💰\n"
            f"*TEMPO PRA PAGAR:* *30 MINUTOS* ⏳\n\n"
            f"*ID DO PAGAMENTO:* `{payment_id}`\n\n"
            f"*👇 CLIQUE EM CIMA PARA COPIAR👇*\n"
            f"`{qr_code_data}`\n\n"
        )

        details_message = escape_markdown_v2(details_message)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("❌ Cancelar Pagamento", callback_data=f"cancel_payment_{message.chat.id}_{message.message_id}"))

        sent_message = bot.send_photo(
            message.chat.id,
            photo=qr_image,
            caption=details_message,
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )

        # Marca o pedido como pendente para o usuário
        pending_pix[user_id] = True
        waiting_for_value[user_id] = False

        # Exclui a mensagem de processamento após o Pix ser enviado
        bot.delete_message(message.chat.id, processing_message.message_id)

        threading.Thread(target=check_payment_periodically, args=(payment_id, message.chat.id, amount, expiration_time, sent_message.message_id, user_id)).start()

    except Exception as e:
        bot.send_message(message.chat.id, f"Erro: {str(e)}")
    finally:
        loop.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_payment_"))
def cancel_payment(call):
    try:
        user_id = call.from_user.id
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Pagamento cancelado ❌", show_alert=True)
        # Remove o pedido pendente
        pending_pix.pop(user_id, None)
        # Reseta o estado de espera por valor
        waiting_for_value.pop(user_id, None)
    except Exception as e:
        print(f"Erro ao cancelar o pagamento: {str(e)}")

def check_payment_periodically(payment_id, chat_id, amount, expiration_time, message_id, user_id):
    sdk = mercadopago.SDK(credentials['access_token'])
    while True:
        payment_response = sdk.payment().get(payment_id)
        payment_info = payment_response.get("response", {})

        if datetime.now() > expiration_time:
            exp_message = escape_markdown_v2("⏳ *O tempo para pagamento expirou.* O QR Code não é mais válido.")
            bot.send_message(chat_id, exp_message, parse_mode='MarkdownV2')
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"Erro ao excluir a mensagem: {str(e)}")
            # Remove o pedido pendente
            pending_pix.pop(user_id, None)
            # Reseta o estado de espera por valor
            waiting_for_value.pop(user_id, None)
            break

        if payment_info.get("status") == "approved":
            date_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            user_message = (
                f"💵 *Recebimento de Pagamento* 💵\n"
                f"*Valor:* *{amount:.2f} BRL*\n"
                f"*Data:* *{date_str}*\n"
                f"*ID de Transação:* `{payment_id}`\n"
                f"✅ *Pagamento aprovado com sucesso!*"
            )
            user_message = escape_markdown_v2(user_message)
            bot.send_message(chat_id, user_message, parse_mode='MarkdownV2')
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"Erro ao excluir a mensagem: {str(e)}")

            # Atualiza o saldo do usuário
            update_user_balance(user_id, amount)
            # Remove o pedido pendente
            pending_pix.pop(user_id, None)
            # Reseta o estado de espera por valor
            waiting_for_value.pop(user_id, None)
            break

        time.sleep(2)

async def generate_payment(price, name, cpf):
    sdk = mercadopago.SDK(credentials['access_token'])
    payment_data = {
        "transaction_amount": float(price),
        "description": "PAGAMENTO VIA PIX",
        "payment_method_id": "pix",
        "payer": {
            "email": "example@example.com",
            "first_name": name,
            "last_name": "SOBRENOME",
            "identification": {
                "type": "CPF",
                "number": cpf
            },
            "address": {
                "zip_code": "65465-000",
                "street_name": "RUA PRIMEIRO DE MAIO",
                "street_number": "SN",
                "neighborhood": "CANTANHEDE",
                "city": "Cantanhede",
                "federal_unit": "MA"
            }
        }
    }

    payment_response = sdk.payment().create(payment_data)
    payment = payment_response.get("response", {})

    if 'point_of_interaction' in payment:
        data = payment['point_of_interaction']['transaction_data']
        return str(data['qr_code']), payment['id']
    else:
        error_message = payment_response.get("message", "ERRO DESCONHECIDO")
        raise Exception(f"ERRO AO GERAR PAGAMENTO: {error_message}")

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    byte_io = io.BytesIO()
    img.save(byte_io)
    byte_io.seek(0)
    return byte_io

def escape_markdown_v2(text):
    special_chars = ['_', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

@bot.message_handler(content_types=['text', 'photo', 'audio', 'document', 'video', 'voice', 'sticker', 'video_note'])
def handle_all_content_types(message):
    user_id = message.from_user.id

    # Ignora a mensagem do comando /start
    if message.text == "/start":
        return  # Não faz nada com a mensagem /start

    # Verifica se o bot está aguardando um valor
    if not waiting_for_value.get(user_id, False):
        try:
            # Apaga a mensagem enviada pelo usuário, independentemente do tipo
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print(f"Erro ao apagar a mensagem: {str(e)}")

# Função para executar o bot com tratamento de erros
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}. Reiniciando o bot...")
            time.sleep(0)  # Aguarda 5 segundos antes de reiniciar

# Chame a função para iniciar o bot
run_bot()
