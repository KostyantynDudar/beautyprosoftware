import os
import requests

# Путь к файлу окружения
ENV_FILE = "/home/public_html/wp-content/uploads/scripts/.cron_env"
LOG_FILE = "/home/public_html/wp-content/uploads/scripts/update_token_log.txt"

# Функция для записи логов
def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    print(message)

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

# Загрузка переменных из .cron_env
load_env(ENV_FILE)

# Чтение конфигурации из переменных окружения
API_URL = "https://api.aihelps.com/v1/auth/database"
PARAMS = {
    "application_id": os.getenv("APPLICATION_ID"),
    "application_secret": os.getenv("APPLICATION_SECRET"),
    "database_code": os.getenv("DATABASE_CODE"),
}

# Проверка наличия всех необходимых переменных
if not all(PARAMS.values()):
    log_message("Ошибка: Отсутствуют необходимые переменные окружения (APPLICATION_ID, APPLICATION_SECRET, DATABASE_CODE)")
    raise ValueError("Не заданы обязательные переменные окружения!")

def get_token():
    """Получение токена через API."""
    try:
        response = requests.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not token:
            raise ValueError("Не удалось получить токен из ответа API")
        log_message(f"Токен успешно получен: {token}")
        return token
    except Exception as e:
        log_message(f"Ошибка при получении токена: {e}")
        return None

def update_cron_env(token):
    """Обновление .cron_env с новым токеном."""
    try:
        env_vars = {}
        # Читаем текущие переменные
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value

        # Обновляем токен
        env_vars["TOKEN"] = token

        # Записываем обратно
        with open(ENV_FILE, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        log_message(f"Токен успешно обновлён в {ENV_FILE}")
    except Exception as e:
        log_message(f"Ошибка при обновлении .cron_env: {e}")

def main():
    log_message("--- Начало обновления токена ---")
    token = get_token()
    if token:
        update_cron_env(token)
    else:
        log_message("Токен не был обновлён.")
    log_message("--- Завершение обновления токена ---")

if __name__ == "__main__":
    main()
