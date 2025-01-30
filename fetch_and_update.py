import requests
import json
import os
import shutil
from datetime import datetime

# Пути к файлам
TOKEN_FILE = "/home/public_html/wp-content/uploads/scripts/.cron_env"
OUTPUT_FILE = "/home/public_html/wp-content/uploads/scripts/services.json"
MAIN_FILE = "/home/public_html/wp-content/uploads/2024/06/services.txt"
LOG_FILE = "/home/public_html/wp-content/uploads/scripts/fetch_update_log.txt"

# API параметры
API_URL = "https://api.aihelps.com/v1/services?fields=name,descriptionPlainText,location_prices,price_currency,category,archive,public,duration,gender"

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Функция логирования
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

# Функция отправки отчёта в Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            log_message("✅ Сообщение успешно отправлено в Telegram.")
        else:
            log_message(f"❌ Ошибка отправки в Telegram: {response.status_code}, {response.text}")
    except Exception as e:
        log_message(f"❌ Ошибка отправки в Telegram: {e}")

# Функция загрузки токена
def get_token():
    if not os.path.exists(TOKEN_FILE):
        log_message("❌ Файл с токеном не найден.")
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("TOKEN="):
                return line.strip().split("=")[1]
    log_message("❌ Токен не найден в файле.")
    return None

# Функция запроса данных
def fetch_services(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        log_message(f"✅ Загружено {len(data)} услуг в {OUTPUT_FILE}")
        return data
    else:
        log_message(f"❌ Ошибка API: {response.status_code} - {response.text}")
        return None

# Функция обновления данных
def update_services():
    if not os.path.exists(MAIN_FILE):
        log_message(f"❌ Основной файл {MAIN_FILE} не найден.")
        return

    # Создание резервной копии
    shutil.copy(MAIN_FILE, f"{MAIN_FILE}.bak")
    log_message(f"📌 Создана резервная копия {MAIN_FILE}.bak")

    with open(MAIN_FILE, "r", encoding="utf-8") as file:
        old_services = {service["id"]: service for service in json.load(file)}

    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        new_services = {service["id"]: service for service in json.load(file)}

    added = []
    removed = []
    updated = []

    # Определяем, что изменилось
    for s_id, service in new_services.items():
        if s_id in old_services:
            if old_services[s_id].get("location_prices") != service.get("location_prices"):
                updated.append(service)
        else:
            added.append(service)

    for s_id in old_services:
        if s_id not in new_services:
            removed.append(old_services[s_id])

    # Запись обновлённых данных
    with open(MAIN_FILE, "w", encoding="utf-8") as file:
        json.dump(list(new_services.values()), file, ensure_ascii=False, indent=4)

    log_message(f"📊 Изменения: +{len(added)} добавлено, -{len(removed)} удалено, ✏ {len(updated)} обновлено.")

    # Отправка отчёта в Telegram
    report_message = (
        f"📊 <b>Анализ обновления услуг:</b>\n"
        f"➕ Новых услуг: <b>{len(added)}</b>\n"
        f"➖ Удалённых услуг: <b>{len(removed)}</b>\n"
        f"✏ Обновлено цен: <b>{len(updated)}</b>\n"
        f"✅ Данные обновлены в <code>{MAIN_FILE}</code>"
    )
    send_telegram_message(report_message)

# Основная функция
def main():
    log_message("--- Начало обновления ---")
    token = get_token()
    if not token:
        log_message("❌ Токен не получен. Завершение.")
        return
    
    services = fetch_services(token)
    if services:
        update_services()
    
    log_message("--- Завершение обновления ---")

if __name__ == "__main__":
    main()
