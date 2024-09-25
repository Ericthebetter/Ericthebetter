import os
import time
import subprocess
import importlib.util
import telebot
import threading
import sys

TOKEN = '7514091632:AAG6fnCt-hoYnuyakVd2Ju3STsPeJOi1k0Y'
AUTHORIZED_ID = 6572589301
bot = telebot.TeleBot(TOKEN)

# Dicionário para armazenar os PIDs dos processos em execução
running_processes = {}
# Dicionário para armazenar os timestamps das modificações dos arquivos
file_mod_times = {}

def send_message(msg):
    bot.send_message(AUTHORIZED_ID, msg)

def install_package(package):
    try:
        send_message(f"Instalando a biblioteca: {package}")  # Mensagem de instalação da biblioteca
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        send_message(f"Biblioteca {package} instalada com sucesso.")  # Mensagem de sucesso
    except Exception:
        send_message(f"Erro ao instalar a biblioteca {package}.")  # Mensagem de erro simplificada
        return False
    return True

def check_and_run_scripts():
    send_message("Bot iniciado.")  # Mensagem de início do bot
    while True:
        for filename in os.listdir('.'):
            if filename.endswith('.py') and filename not in ['bot.py', '.pythonstartup.py', 'loop.py']:
                # Verifica se o arquivo foi modificado
                current_mod_time = os.path.getmtime(filename)
                if filename not in file_mod_times:
                    file_mod_times[filename] = current_mod_time
                elif file_mod_times[filename] != current_mod_time:
                    # Arquivo modificado
                    if filename in running_processes:
                        running_processes[filename].terminate()  # Termina o processo
                        send_message(f"Arquivo modificado: {filename}. Execução parada.")
                        del running_processes[filename]

                    file_mod_times[filename] = current_mod_time
                    time.sleep(3)  # Espera 3 segundos antes de reexecutar

                # Verifica se o processo está em execução
                if filename not in running_processes or running_processes[filename].poll() is not None:
                    try:
                        with open(filename) as f:
                            code = f.read()
                            # Verifica as bibliotecas importadas
                            imports = set()
                            for line in code.splitlines():
                                if line.startswith('import ') or line.startswith('from '):
                                    module = line.split()[1].split('.')[0]  # Obtem o nome do módulo
                                    imports.add(module)

                            # Instala as bibliotecas, se necessário
                            for package in imports:
                                if not importlib.util.find_spec(package):
                                    if not install_package(package):
                                        os.remove(filename)
                                        send_message(f"Arquivo {filename} removido devido a erro na instalação da biblioteca {package}")
                                        break
                            else:
                                # Executa o arquivo em um novo processo
                                process = subprocess.Popen([sys.executable, filename])
                                running_processes[filename] = process
                                send_message(f"Executado o arquivo: {filename} com PID {process.pid}")

                    except Exception as e:
                        send_message(f"Erro ao executar {filename}: {str(e)}")

        time.sleep(1)

def monitor_directory():
    previous_files = set(os.listdir('.'))
    while True:
        time.sleep(1)
        current_files = set(os.listdir('.'))

        # Verifica arquivos removidos
        removed_files = previous_files - current_files
        for removed in removed_files:
            if removed.endswith('.py'):
                send_message(f"Arquivo removido: {removed}")
                if removed in running_processes:
                    running_processes[removed].terminate()  # Termina o processo
                    del running_processes[removed]  # Remove do dicionário
                if removed in file_mod_times:
                    del file_mod_times[removed]  # Remove do dicionário de modificações

        # Atualiza a lista de arquivos
        previous_files = current_files

# Adicione essa função para parar todos os processos em execução
def stop_all_processes():
    for filename, process in running_processes.items():
        process.terminate()
        process.wait()  # Aguarda o processo terminar
    running_processes.clear()  # Limpa o dicionário de processos em execução

# Adicione esse comando para o bot
@bot.message_handler(commands=['reload'])
def handle_reload(message):
    send_message("Recarregando scripts...")  # Mensagem de início do reload
    stop_all_processes()  # Para todos os processos
    time.sleep(1)  # Aguarda um segundo para garantir que os processos pararam
    send_message("Todos os processos parados. Reiniciando scripts...")  # Mensagem de confirmação
    check_and_run_scripts()  # Executa novamente todos os scripts

# Inicia as threads para monitorar os scripts e diretórios assim que o bot é iniciado
threading.Thread(target=check_and_run_scripts).start()
threading.Thread(target=monitor_directory).start()

# Função para executar o bot com tratamento de erros
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}. Reiniciando o bot...")
            time.sleep(0)  # Aguarda 0 segundos antes de reiniciar

# Chame a função para iniciar o bot
run_bot()
