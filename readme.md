# TelegramBot 🤖

Простий Telegram-бот, написаний на Python, який дозволяє обробляти повідомлення користувачів, надавати корисну інформацію, працювати з клавіатурами та командами.

## 📌 Основні можливості

- Обробка команд користувача
- Підтримка декількох мов
- Використання JSON-файлів для збереження даних
- Надсилання IP-адреси, скріншотів, контактної інформації
- Панель адміністратора
````
## 📁 Структура проекту

mytgbot/
├── bot.py # Основний файл запуску бота
├── handlers.py # Обробники повідомлень та callback'ів
├── keyboards.py # Файли з клавіатурами
├── utils.py # Допоміжні функції
├── admins.json # Список адміністраторів
├── contacts.json # Контактна інформація
├── court_schedule.json # Розклад судів
├── faq.json # Часті запитання
├── languages.json # Дані про підтримувані мови
````


## 🛠 Встановлення

1. Клонуйте репозиторій:
```
   git clone https://github.com/tarasmakarenko/mytgbot.git
   cd mytgbot
```
Створіть віртуальне середовище та активуйте його:
````
python -m venv venv
source venv/bin/activate        # для Linux/macOS
venv\Scripts\activate           # для Windows
````

Встановіть залежності:

``````
pip install -r requirements.txt
Якщо файл requirements.txt відсутній, створіть його та додайте:
``````

````
pyTelegramBotAPI
requests
pyscreenshot
````

⚙️ Налаштування
Відкрийте bot.py та вставте свій токен:


bot = telebot.TeleBot('ВАШ_TELEGRAM_TOKEN')
Оновіть файли з даними:
````
admins.json — ваші Telegram user ID

contacts.json, faq.json, court_schedule.json — вміст, який бачить користувач

languages.json — налаштування доступних мов
````
🚀 Запуск
Запустіть бота командою:
```
python bot.py
```