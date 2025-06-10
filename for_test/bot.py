"""
Основний файл для запуску Telegram-бота.
Ініціалізує бота та реєструє всі обробники повідомлень.
"""
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
import logging

logging.basicConfig(level=logging.INFO)

async def on_start(app):
    """
    Асинхронна функція, яка виконується при запуску бота.
    """
    print("✅ Бот запущено!")

def main():
    """
    Головна функція для ініціалізації та запуску Telegram-бота.
    """
    # Ініціалізація ApplicationBuilder з токеном бота та функцією post_init
    # Токен бота має бути замінений на ваш реальний токен.
    application = ApplicationBuilder().token("7884159343:AAEEEjfqvaAjFxedjsnvc1ManpXQ7pHP2FM").post_init(on_start).build()

    # Реєстрація всіх обробників повідомлень з модуля handlers
    register_handlers(application)

    # Запуск бота в режимі довгого опитування (polling)
    # Це дозволяє боту постійно слухати нові повідомлення від Telegram API
    application.run_polling()

if __name__ == "__main__":
    main()

