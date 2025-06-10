"""
Основний файл для запуску Telegram-бота.

Цей модуль відповідає за ініціалізацію бота,
реєстрацію всіх обробників повідомлень та запуск
процесу прослуховування вхідних оновлень від Telegram API.
"""
import logging
import os
from logging.handlers import RotatingFileHandler # Для ротації логів
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from for_test.utils import load_language_message, send_admin_notification # Для локалізованих повідомлень

# --- Налаштування логування ---
# Визначаємо шлях до лог-файлу. Рекомендується використовувати абсолютний шлях
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot.log')

# Отримуємо рівень логування зі змінної середовища, за замовчуванням INFO
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
# Перетворюємо рядок на рівень логування
NUMERIC_LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.INFO)

# Створюємо логер
logger = logging.getLogger(__name__)
logger.setLevel(NUMERIC_LOG_LEVEL)

# Створюємо форматувальник для логів: час, ім'я логера, рівень, повідомлення
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Створюємо консольний обробник (для виводу в термінал)
console_handler = logging.StreamHandler()
console_handler.setLevel(NUMERIC_LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Створюємо файловий обробник з ротацією (за розміром)
# Максимальний розмір файлу 5 MB, зберігаємо 5 останніх файлів
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'
)
file_handler.setLevel(NUMERIC_LOG_LEVEL)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- Кінець налаштування логування ---


async def on_start(app):
    """
    Асинхронна функція, яка виконується при успішному запуску бота.

    Виводить повідомлення про те, що бот успішно запущений.

    :param app: Об'єкт Application, що представляє екземпляр бота.
    :type app: telegram.ext.Application
    """
    logger.info("✅ Бот запущено!")

def main():
    """
    Головна функція для ініціалізації та запуску Telegram-бота.

    Створює екземпляр Application, реєструє в ньому всі обробники
    та запускає бота в режимі довгого опитування (polling),
    що дозволяє йому постійно слухати нові повідомлення.
    """
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        logger.critical("ERR_APP_001: BOT_TOKEN environment variable is not set. Bot cannot start.")
        # Тут неможливо відправити адмін-сповіщення, бо бот ще не ініціалізовано
        return

    application = ApplicationBuilder().token(bot_token).post_init(on_start).build()

    register_handlers(application)

    try:
        logger.info("Запуск polling...")
        application.run_polling()
    except Exception as e:
        logger.critical(f"ERR_APP_002: Бот завершив роботу через критичну помилку: {e}", exc_info=True)
        # Намагаємося надіслати сповіщення адміністратору, якщо бот хоч якось функціонував
        # (хоча при критичній помилці запуску це може не спрацювати)
        admin_message = load_language_message('uk', 'admin_critical_error_notification')
        send_admin_notification(application.bot, f"{admin_message}\nПомилка: {e}")


if __name__ == "__main__":
    main()
