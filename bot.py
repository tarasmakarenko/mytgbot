from telegram.ext import ApplicationBuilder
from handlers import register_handlers
import logging

logging.basicConfig(level=logging.INFO)

async def on_start(app):
    print("✅ Бот запущено!")

def main():
    application = ApplicationBuilder().token("7884159343:AAEEEjfqvaAjFxedjsnvc1ManpXQ7pHP2FM").post_init(on_start).build()
    register_handlers(application)
    application.run_polling()

if __name__ == "__main__":
    main()
