"""
Модуль утиліт для Telegram-бота.
Містить допоміжні функції для роботи з файлами, датами та даними.
"""
import json
from datetime import datetime, timedelta

def load_language(user_id: int) -> str:
    """
    Завантажує обрану мову для користувача.
    Повертає 'uk' за замовчуванням у разі помилки або відсутності даних.
    """
    try:
        with open("languages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(user_id), "uk")
    except (FileNotFoundError, json.JSONDecodeError):
        # Ловимо конкретні винятки, якщо файл не знайдено або він не є дійсним JSON
        return "uk"

def set_language(user_id: int, lang: str):
    """
    Зберігає обрану мову для користувача.
    """
    data = {}
    try:
        with open("languages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass # Файл може не існувати або бути пустим, і це нормально для першого запису

    data[str(user_id)] = lang
    with open("languages.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id: int) -> bool:
    """
    Перевіряє, чи є користувач адміністратором.
    """
    try:
        with open("admins.json", "r", encoding="utf-8") as f:
            admins = json.load(f)
        return user_id in admins
    except (FileNotFoundError, json.JSONDecodeError):
        return False # Якщо файл не знайдено або він пошкоджений, адміністраторів немає

def get_faq_answer(lang: str, question: str) -> str:
    """
    Отримує відповідь на питання з файлу faq.json для обраної мови.
    """
    try:
        with open("faq.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[lang].get(question, "⚠️ Вибачте, відповіді не знайдено.")
    except (FileNotFoundError, json.JSONDecodeError):
        return "⚠️ Вибачте, сталася помилка при завантаженні FAQ."

def get_court_info(lang: str) -> dict:
    """
    Отримує інформацію про суд з файлу court_info.json для обраної мови.
    """
    try:
        with open("court_info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[lang]
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "address": "Інформація недоступна",
            "work_time": "Інформація недоступна",
            "phone": "Інформація недоступна",
            "email": "Інформація недоступна"
        }

def get_available_dates() -> list:
    """
    Генерує список доступних дат для запису (будні дні протягом 14 днів).
    """
    today = datetime.now().date()
    # Створюємо список, переконуючись, що кожен елемент вміщується в ліміт рядка
    dates = []
    for i in range(14):
        current_date = today + timedelta(days=i)
        if current_date.weekday() < 5:  # Понеділок (0) - П'ятниця (4)
            dates.append(str(current_date))
    return dates

def get_available_times_for_date(selected_date: str) -> list:
    """
    Генерує список доступних часових слотів для вибраної дати.
    Виключає обідню перерву (13:00).
    """
    times = []
    for hour in range(9, 17):
        if hour == 13:
            continue
        times.append(f"{selected_date} {hour:02d}:00") # Додаємо ":02d" для форматування годин як "09" замість "9"
    return times

def save_appointment(user_id: int, name: str, time: str):
    """
    Зберігає інформацію про запис на консультацію до файлу appointments.json.
    """
    data = []
    try:
        with open("appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass # Файл може не існувати або бути пустим, і це нормально для першого запису

    data.append({"user_id": user_id, "name": name, "time": time})
    with open("appointments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_appointments_for_admin() -> str:
    """
    Отримує список всіх записів для адміністратора.
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return "Немає записів."
        return "\n".join([f"— {r['name']}, {r['time']}" for r in data])
    except (FileNotFoundError, json.JSONDecodeError):
        return "Немає записів."

def get_appointments_for_user() -> str:
    """
    Отримує список записів для конкретного користувача.
    (Ця функція була у вихідному коді, але не використовувалась у handlers.py)
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # Фільтруємо записи по user_id, якщо це необхідно для відображення користувачеві
        # Наразі просто повертаємо список зайнятих часів, як у вихідному коді
        return "\n".join([f"— {r['time']} ❌ Зайнято" for r in data])
    except (FileNotFoundError, json.JSONDecodeError):
        return "No appointments yet."

