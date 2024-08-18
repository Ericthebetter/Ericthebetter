from pyrogram import Client, filters
import mercadopago
from datetime import datetime, timedelta
import asyncio

# Configurações do Mercado Pago
credentials = {
    'access_token': 'acessoaquu'
}

app = Client("seupyrogramaqui")

# Dicionário global para mapear payment_id ao chat_id e message_id
payment_mapping = {}

async def generate_payment(price):
    sdk = mercadopago.SDK(credentials['access_token'])
    payment_data = {
        "transaction_amount": float(price),
        "description": "Pagamento via Pix",
        "payment_method_id": "pix",
        "payer": {
            "email": "example@example.com",  # Coloque o email do pagador aqui
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "identification": {
                "type": "CPF",
                "number": "xxxx"
            },
            "address": {
                "zip_code": "xxxx",
                "street_name": "rua aleatório",
                "street_number": "SN",
                "neighborhood": "sn",
                "city": "sn",
                "federal_unit": "sn"
            }
        }
    }
    
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response.get("response", {})

    if 'point_of_interaction' in payment:
        data = payment['point_of_interaction']['transaction_data']
        creation_time = datetime.now()  # Horário de criação do pagamento
        expiration_time = creation_time + timedelta(minutes=30)  # Horário de expiração

        return {
            'clipboard': str(data['qr_code']),
            'expiration_time': expiration_time,
            'payment_id': payment['id'],
            'creation_time': creation_time,  # Armazena o horário de criação
            'price': price  # Armazena o valor do pagamento
        }
    else:
        error_message = payment_response.get("message", "Erro desconhecido")
        raise Exception(f"Erro ao gerar pagamento: {error_message}")

@app.on_message(filters.command("pagar"))
async def pay_command(client, message):
    try:
        if len(message.command) != 2:
            await message.reply("Uso correto: /pagar <valor>")
            return
        
        valor = float(message.command[1])
        payment_info = await generate_payment(valor)

        chat_id = message.chat.id
        qr_message = await message.reply(f"**Código Pix gerado:**\n`{payment_info['clipboard']}`")

        # Armazena o mapping com o payment_id associado ao chat_id e message_id
        payment_mapping[payment_info['payment_id']] = {
            'chat_id': chat_id,
            'message_id': qr_message.id,  # Acesse o id da mensagem retornada
            'user_id': chat_id,  # Armazena o ID do usuário
            'creation_time': payment_info['creation_time'],  # Armazena o horário de criação
            'valor': valor  # Armazena o valor solicitado
        }

        # Log da geração do Pix
        transaction_id = f"{chat_id}{payment_info['creation_time'].strftime('%d%m%Y')}{payment_info['creation_time'].strftime('%H%M%S')}{int(valor)}"
        
        print("Log de geração Pix!")
        print(f"Data: {payment_info['creation_time'].strftime('%d/%m/%Y')}")
        print(f"ID do usuário: {chat_id}")  # ID do usuário em segundo lugar
        print(f"Valor a pagar: {valor}")  # Valor a pagar logo abaixo do ID do usuário
        print(f"Hora: {payment_info['creation_time'].strftime('%H:%M:%S')}")
        print(f"ID de pagamento: aqui é o id da trans: {payment_info['payment_id']}")
        print(f"ID da transação: {transaction_id}")
        print()  # Linha em branco para separar logs de diferentes usuários

        # Espera 30 minutos e depois verifica o status
        await asyncio.sleep(1800)  # 30 minutos em segundos

        current_time = datetime.now()
        if current_time < payment_info['expiration_time']:
            await qr_message.edit("Pagamento efetuado!")  # Edita a mensagem se o pagamento for considerado efetuado
        else:
            await qr_message.edit("Pagamento falhou.")  # Edita a mensagem se o tempo expirou

    except Exception as e:
        await message.reply(f'Erro: {str(e)}')

app.run()
