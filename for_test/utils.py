"""
Модуль утиліт для Telegram-бота.

Містить допоміжні функції для роботи з файлами JSON (зберігання та читання даних),
генерації дат і часу, перевірки прав адміністратора та управління мовними налаштуваннями.
"""
import json # Стандартна бібліотека
from datetime import datetime, timedelta # Стандартна бібліотека

def load_language(user_id: int) -> str:
    """Завантажує обрану мову для користувача з файлу languages.json.

    Якщо файл `languages.json` не знайдено або він не є дійсним JSON,
    або якщо мова для конкретного користувача не збережена,
    повертає українську мову ('uk') за замовчуванням.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :returns: Код мови ('uk' або 'en').
    :rtype: str
    """
    try:
        with open("languages.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return data.get(str(user_id), "uk")
    except (FileNotFoundError, json.JSONDecodeError):
        # Ловимо конкретні винятки, якщо файл не знайдено або він не є дійсним JSON
        return "uk"

def set_language(user_id: int, lang: str):
    """Зберігає обрану мову для користувача у файлі languages.json.

    Якщо файл `languages.json` не існує або пошкоджений, він буде створений
    або перевизначений.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param lang: Код мови для збереження ('uk' або 'en').
    :type lang: str
    """
    data = {}
    try:
        with open("languages.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (FileNotFoundError, json.JSONDecodeError):
        pass # Файл може не існувати або бути пустим, і це нормально для першого запису

    data[str(user_id)] = lang
    with open("languages.json", "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, ensure_ascii=False, indent=2)

def is_admin(user_id: int) -> bool:
    """Перевіряє, чи є користувач адміністратором, згідно з файлом admins.json.

    Читає список ID адміністраторів з `admins.json`. Якщо файл не знайдено
    або він пошкоджений, повертає False (користувач не є адміністратором).

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :returns: True, якщо користувач є адміністратором, False - в іншому випадку.
    :rtype: bool
    """
    try:
        with open("admins.json", "r", encoding="utf-8") as file_handle:
            admins = json.load(file_handle)
        return user_id in admins
    except (FileNotFoundError, json.JSONDecodeError):
        return False # Якщо файл не знайдено або він пошкоджений, адміністраторів немає

def get_faq_answer(lang: str, question: str) -> str:
    """Отримує відповідь на питання з файлу faq.json для обраної мови.

    Читає базу питань та відповідей з `faq.json`. Якщо питання не знайдено
    для вказаної мови або файл пошкоджений, повертає повідомлення про помилку.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :param question: Текст питання, на яке потрібно знайти відповідь.
    :type question: str
    :returns: Текст відповіді на питання або повідомлення про помилку.
    :rtype: str
    """
    try:
        with open("faq.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return data[lang].get(question, "⚠️ Вибачте, відповіді не знайдено.")
    except (FileNotFoundError, json.JSONDecodeError):
        return "⚠️ Вибачте, сталася помилка при завантаженні FAQ."

def get_court_info(lang: str) -> dict:
    """Отримує інформацію про суд з файлу court_info.json для обраної мови.

    Читає контактну та загальну інформацію про судову установу з `court_info.json`.
    Якщо файл пошкоджений або інформація недоступна, повертає словник з
    повідомленнями про недоступність.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :returns: Словник з інформацією про суд (адреса, графік, телефон, email).
    :rtype: dict
    """
    try:
        with open("court_info.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return data[lang]
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "address": "Інформація недоступна",
            "work_time": "Інформація недоступна",
            "phone": "Інформація недоступна",
            "email": "Інформація недоступна"
        }

def get_available_dates() -> list:
    """Генерує список доступних дат для запису.

    Повертає список рядків з датами (у форматі YYYY-MM-DD)
    наступних 14 календарних днів, виключаючи вихідні (суботу та неділю).

    :returns: Список доступних дат.
    :rtype: list[str]
    """
    today = datetime.now().date()
    dates = []
    for day_offset in range(14):
        current_date = today + timedelta(days=day_offset)
        if current_date.weekday() < 5:  # Понеділок (0) - П'ятниця (4)
            dates.append(str(current_date))
    return dates

def get_available_times_for_date(selected_date: str) -> list:
    """Генерує список доступних часових слотів для вибраної дати.

    Формує список часу з 9:00 до 16:00 (з кроком в 1 годину),
    виключаючи 13:00 (обідня перерва).

    :param selected_date: Вибрана дата у форматі YYYY-MM-DD.
    :type selected_date: str
    :returns: Список доступних часових слотів у форматі "YYYY-MM-DD HH:MM".
    :rtype: list[str]
    """
    times = []
    for hour in range(9, 17):
        if hour == 13:
            continue
        times.append(f"{selected_date} {hour:02d}:00")
    return times

def save_appointment(user_id: int, name: str, time: str):
    """Зберігає інформацію про запис на консультацію до файлу appointments.json.

    Додає новий запис (user_id, ПІБ, дата та час) до існуючого списку записів.
    Якщо файл `appointments.json` не існує або пошкоджений, він буде створений
    або перевизначений.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param name: Повне ім'я (ПІБ) користувача, який записується.
    :type name: str
    :param time: Вибраний час запису у форматі "YYYY-MM-DD HH:MM".
    :type time: str
    """
    data = []
    try:
        with open("appointments.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (FileNotFoundError, json.JSONDecodeError):
        pass # Файл може не існувати або бути пустим, і це нормально для першого запису

    data.append({"user_id": user_id, "name": name, "time": time})
    with open("appointments.json", "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, ensure_ascii=False, indent=2)

def get_appointments_for_admin() -> str:
    """Отримує відформатований список всіх записів для адміністратора.

    Читає всі записи з `appointments.json` та повертає їх у вигляді
    одного рядка, де кожен запис відображений на новому рядку.

    :returns: Рядок з усіма записами або повідомлення про їх відсутність.
    :rtype: str
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not data:
            return "Немає записів."
        return "\n".join([f"— {record['name']}, {record['time']}" for record in data])
    except (FileNotFoundError, json.JSONDecodeError):
        return "Немає записів."

def get_appointments_for_user() -> str:
    """Отримує відформатований список записів для конкретного користувача.

    (Ця функція була у вихідному коді, але наразі не використовується
    безпосередньо в обробниках бота для відображення користувачеві його власних записів.
    Повертає загальний список зайнятих часів, як у вихідному коді.)

    :returns: Рядок з усіма зайнятими часами або повідомлення про їх відсутність.
    :rtype: str
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        # Фільтруємо записи по user_id, якщо це необхідно для відображення користувачеві
        # Наразі просто повертаємо список зайнятих часів, як у вихідному коді
        return "\n".join([f"— {record['time']} ❌ Зайнято" for record in data])
    except (FileNotFoundError, json.JSONDecodeError):
        return "No appointments yet."
