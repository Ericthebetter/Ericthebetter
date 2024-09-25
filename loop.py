import subprocess
import psutil
import time
import atexit
import os
import sys

def is_running(script_name):
    # Verifica se o script está em execução
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if script_name in process.info['cmdline']:
            return True
    return False

def run_script(script_name):
    # Executa o script
    subprocess.Popen(['python', script_name])

def restart_script():
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    while True:
        if not is_running('bot.py'):
            print("Iniciando bot.py...")
            run_script('bot.py')

        time.sleep(35)  # Espera 35 segundos antes de verificar novamente

    atexit.register(restart_script)
