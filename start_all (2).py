# -*- coding: utf-8 -*-
import subprocess
import os
from datetime import datetime
import requests

# Пути к файлам
ENV_FILE = "/home/veronicaplus/public_html/wp-content/uploads/scripts/.cron_env"
LOG_FILE = "/home/veronicaplus/public_html/wp-content/uploads/scripts/fetch_services_log.txt"

# Файл с токеном
UPDATE_TOKEN_SCRIPT = "update_token.py"

# Новый объединённый скрипт для загрузки и обновления цен
FETCH_AND_UPDATE_SCRIPT = "fetch_and_update.py"

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Функция логирования
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Проверка, если сегодня 1-е число месяца, то очищаем лог-файл
    if datetime.now().day == 1:
        with open(LOG_FILE, "w", encoding="utf-8") as log:
            log.write(f"[{timestamp}] 🔄 Очистка логов: новый месяц\n")
        print(f"[{timestamp}] 🔄 Очистка логов: новый месяц")

    # Запись нового сообщения в лог
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

# Функция для загрузки переменных из .cron_env
def load_env(file_path):
    if os.path.exists(file_path):
        log_message(f"Файл {file_path} найден. Начинаем загрузку переменных...")
        with open(file_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
                        log_message(f"Переменная загружена: {key}={value}")
                    except ValueError:
                        log_message(f"Ошибка разбора строки: {line.strip()}")
    else:
        log_message(f"Файл {file_path} не найден. Переменные не загружены.")

# Загрузка переменных окружения
load_env(ENV_FILE)

# Функция выполнения скрипта
def run_script(script_name):
    try:
        log_message(f"Запуск скрипта: {script_name}")
        result = subprocess.run(["python3", script_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log_message(f"Скрипт {script_name} выполнен успешно. Вывод:\n{result.stdout.decode('utf-8')}")
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        log_message(f"Ошибка при выполнении скрипта {script_name}. Ошибка:\n{e.stderr.decode('utf-8') if e.stderr else str(e)}")
        return ""

# Функция отправки сообщения в Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            log_message("Сообщение успешно отправлено в Telegram.")
        else:
            log_message(f"Ошибка при отправке сообщения в Telegram: {response.status_code}, {response.text}")
    except Exception as e:
        log_message(f"Ошибка при отправке сообщения в Telegram: {e}")

# Основной процесс
if __name__ == "__main__":
    log_message("--- Начало выполнения процесса ---")

    # Запуск обновления токена
    run_script(UPDATE_TOKEN_SCRIPT)

    # Запуск обновления услуг и цен
    run_script(FETCH_AND_UPDATE_SCRIPT)

    log_message("--- Завершение выполнения процесса ---")

    # Отправка уведомления в Telegram
    send_telegram_message(f"<b>✅ Оновлення завершено!</b>\nДані оновлені в `services-202406061830.txt`")
