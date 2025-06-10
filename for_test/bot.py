"""
Основний файл для запуску Telegram-бота.

Цей модуль відповідає за ініціалізацію бота,
реєстрацію всіх обробників повідомлень та запуск
процесу прослуховування вхідних оновлень від Telegram API.
"""
import logging # Стандартна бібліотека

from telegram.ext import ApplicationBuilder # Стороння бібліотека
from handlers import register_handlers # Локальний модуль

logging.basicConfig(level=logging.INFO)

async def on_start(app):
    """
    Асинхронна функція, яка виконується при успішному запуску бота.

    Виводить повідомлення про те, що бот успішно запущений.

    :param app: Об'єкт Application, що  представляє екземпляр бота.
    :type app: telegram.ext.Application
    """
    print("✅ Бот запущено!")

def main():
    """
    Головна функція для ініціалізації та запуску Telegram-бота.

    Створює екземпляр Application, реєструє в ньому всі обробники
    та запускає бота в режимі довгого опитування (polling),
    що дозволяє йому постійно слухати нові повідомлення.
    """
    # Ініціалізація ApplicationBuilder з токеном бота та функцією post_init
    # Токен бота має бути замінений на ваш реальний токен.
    application = ApplicationBuilder().token(
        "7884159343:AAEEEjfqvaAjFxedjsnvc1ManpXQ7pHP2FM"
    ).post_init(on_start).build()

    # Реєстрація всіх обробників повідомлень з модуля handlers
    register_handlers(application)

    # Запуск бота в режимі довгого опитування (polling)
    # Це дозволяє боту постійно слухати нові повідомлення від Telegram API
    application.run_polling()


if __name__ == "__main__":
    main()
