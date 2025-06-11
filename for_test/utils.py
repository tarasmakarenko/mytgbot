"""
Модуль утиліт для Telegram-бота.

Містить допоміжні функції для роботи з файлами JSON (зберігання та читання даних),
генерації дат і часу, перевірки прав адміністратора та управління мовними налаштуваннями.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Union

# Створюємо логер для цього модуля
logger = logging.getLogger(__name__)

# --- Локалізація повідомлень ---
_messages_data: Dict[str, Dict[str, str]] = {}
MESSAGES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'messages.json')

def _load_messages():
    """Внутрішня функція для завантаження локалізованих повідомлень."""
    global _messages_data # pylint: disable=global-statement
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as file_handle:
            _messages_data = json.load(file_handle)
        logger.info("Messages data loaded successfully.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"ERR_UTIL_001: Critical error loading messages.json: {e}", exc_info=True)
        # У випадку критичної помилки, ініціалізуємо базовими повідомленнями
        _messages_data = {
            "uk": {
                "generic_user_error": "Вибачте, сталася неочікувана помилка. Будь ласка, спробуйте пізніше.",
                "generic_user_error_with_contact": "Вибачте, сталася неочікувана помилка. Будь ласка, спробуйте пізніше або зверніться до адміністратора.",
                "admin_critical_error_notification": "Критична помилка в роботі бота!",
                "choose_language": "🌐 Оберіть мову / Choose language:",
                "language_set_success": "✅ Мову встановлено!",
                "choose_faq_question": "❓ Оберіть питання:",
                "faq_answer_not_found": "⚠️ Вибачте, відповіді на це питання не знайдено. Спробуйте інше питання або зверніться до адміністратора.",
                "data_load_error": "⚠️ Вибачте, сталася помилка при завантаженні даних. Будь ласка, спробуйте пізніше.",
                "no_schedule_available": "Наразі розклад засідань відсутній.",
                "court_schedule_title": "📅 Розклад засідань:",
                "case": "Справа",
                "judge": "Суддя",
                "no_contacts_available": "Наразі контакти інших установ відсутні.",
                "other_contacts_title": "📞 Контакти інших установ:",
                "enter_full_name": "📝 Введіть ПІБ для запису:",
                "choose_date": "📅 Оберіть дату:",
                "no_dates_available": "На жаль, доступних дат для запису немає.",
                "choose_time": "⏰ Оберіть час:",
                "no_times_available": "На жаль, доступного часу для запису на цю дату немає.",
                "appointment_booked_success": "✅ Ви успішно записані!",
                "no_name_provided": "Без імені",
                "unrecognized_command": "🤷‍♀️ Вибачте, я не зрозумів вашу команду. Будь ласка, оберіть опцію з меню або використайте /start.",
                "unauthorized_access": "🚫 Вибачте, у вас немає доступу до цієї команди.",
                "admin_panel_greeting": "Привіт, адміністраторе! Це адмін-панель.",
                "address": "Адреса",
                "schedule": "Графік",
                "phone": "Телефон",
                "email": "Email",
                "no_appointments_admin": "Немає записів.",
                "no_appointments_user": "No appointments yet."
            },
            "en": {
                "generic_user_error": "Sorry, an unexpected error occurred. Please try again later.",
                "generic_user_error_with_contact": "Sorry, an unexpected error occurred. Please try again later or contact the administrator.",
                "admin_critical_error_notification": "Critical error in bot operation!",
                "choose_language": "🌐 Оберіть мову / Choose language:",
                "language_set_success": "✅ Language set!",
                "choose_faq_question": "❓ Choose a question:",
                "faq_answer_not_found": "⚠️ Sorry, no answer found for this question. Try another question or contact the administrator.",
                "data_load_error": "⚠️ Sorry, there was an error loading data. Please try again later.",
                "no_schedule_available": "No hearing schedule available at the moment.",
                "court_schedule_title": "📅 Hearing Schedule:",
                "case": "Case",
                "judge": "Judge",
                "no_contacts_available": "No contacts for other institutions available at the moment.",
                "other_contacts_title": "📞 Other Institutions Contacts:",
                "enter_full_name": "📝 Enter full name for appointment:",
                "choose_date": "📅 Choose a date:",
                "no_dates_available": "Sorry, no available dates for appointment.",
                "choose_time": "⏰ Choose a time:",
                "no_times_available": "Sorry, no available times for this date.",
                "appointment_booked_success": "✅ You are successfully booked!",
                "no_name_provided": "No name provided",
                "unrecognized_command": "🤷‍♀️ Sorry, I didn't understand your command. Please choose an option from the menu or use /start.",
                "unauthorized_access": "🚫 Sorry, you do not have access to this command.",
                "admin_panel_greeting": "Hello, admin! This is the admin panel.",
                "address": "Address",
                "schedule": "Schedule",
                "phone": "Phone",
                "email": "Email",
                "no_appointments_admin": "No appointments.",
                "no_appointments_user": "No appointments yet."
            }
        }
    except Exception as ex:
        logger.critical(f"ERR_UTIL_002: Very critical error during message loading fallback: {ex}", exc_info=True)
        _messages_data = {
            "uk": {"generic_user_error": "System error. Please try again later."},
            "en": {"generic_user_error": "System error. Please try again later."}
        }

_load_messages()

def load_language_message(lang_code: str, message_key: str) -> str:
    """
    Завантажує локалізоване повідомлення за ключем та кодом мови.
    Повертає повідомлення англійською, якщо українське недоступне, або загальне повідомлення про помилку.

    :param lang_code: Код мови (наприклад, 'uk' або 'en').
    :type lang_code: str
    :param message_key: Ключ повідомлення в словнику повідомлень.
    :type message_key: str
    :returns: Локалізоване повідомлення.
    :rtype: str
    """
    logger.debug(f"Attempting to load message '{message_key}' for language '{lang_code}'.")

    if lang_code not in _messages_data:
        logger.warning(f"WARN_UTIL_001: Language '{lang_code}' not found in messages data. Falling back to 'en'.")
        lang_code = 'en'

    message = _messages_data.get(lang_code, {}).get(message_key)
    if message is None:
        logger.error(
            f"ERR_UTIL_003: Message key '{message_key}' not found for language '{lang_code}'. "
            "Context: load_language_message failure."
        )
        return _messages_data.get(lang_code, {}).get('generic_user_error', "Error: message not found.")
    return message


# --- Функції бота ---

def load_language(user_id: int, correlation_id: str = "N/A") -> str:
    """
    Завантажує обрану мову для користувача з файлу languages.json.
    Повертає 'uk' за замовчуванням у разі помилки або відсутності даних.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Код мови ('uk' або 'en').
    :rtype: str
    """
    try:
        with open("languages.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        logger.debug(
            f"[REQ_ID:{correlation_id}] Loaded language '{data.get(str(user_id))}' for user {user_id}."
        )
        return data.get(str(user_id), "uk")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(
            f"WARN_UTIL_002 [REQ_ID:{correlation_id}]: Failed to load languages.json for user {user_id}. Error: {e}"
        )
        return "uk"

def set_language(user_id: int, lang: str, correlation_id: str = "N/A"):
    """
    Зберігає обрану мову для користувача у файлі languages.json.

    Якщо файл `languages.json` не існує або пошкоджений, він буде створений
    або перевизначений.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param lang: Код мови для збереження ('uk' або 'en').
    :type lang: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    """
    data = {}
    try:
        if os.path.exists("languages.json"):
            with open("languages.json", "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
    except json.JSONDecodeError as e:
        logger.warning(
            f"WARN_UTIL_003 [REQ_ID:{correlation_id}]: languages.json is corrupted for user {user_id}. "
            f"Resetting data. Error: {e}"
        )
    except FileNotFoundError:
        logger.info(
            f"[REQ_ID:{correlation_id}] languages.json not found for user {user_id}. Creating new file."
        )
        pass

    data[str(user_id)] = lang
    try:
        with open("languages.json", "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)
        logger.debug(f"[REQ_ID:{correlation_id}] Language '{lang}' saved for user {user_id}.")
    except IOError as e:
        logger.error(
            f"ERR_UTIL_004 [REQ_ID:{correlation_id}]: Failed to write to languages.json "
            f"for user {user_id}. Error: {e}", exc_info=True
        )


def is_admin(user_id: int, correlation_id: str = "N/A") -> bool:
    """
    Перевіряє, чи є користувач адміністратором, згідно з файлом admins.json.

    Читає список ID адміністраторів з `admins.json`. Якщо файл не знайдено
    або він пошкоджений, повертає False (користувач не є адміністратором).

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: True, якщо користувач є адміністратором, False - в іншому випадку.
    :rtype: bool
    """
    try:
        with open("admins.json", "r", encoding="utf-8") as file_handle:
            admins = json.load(file_handle)
        is_user_admin = user_id in admins
        logger.debug(f"[REQ_ID:{correlation_id}] User {user_id} is admin: {is_user_admin}.")
        return is_user_admin
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(
            f"WARN_UTIL_004 [REQ_ID:{correlation_id}]: admins.json not found or corrupted. "
            f"No admins defined. Error: {e}"
        )
        return False


def get_faq_answer(lang: str, question: str, correlation_id: str = "N/A") -> str:
    """
    Отримує відповідь на питання з файлу faq.json для обраної мови.

    Читає базу питань та відповідей з `faq.json`. Якщо питання не знайдено
    для вказаної мови або файл пошкоджений, повертає повідомлення про помилку.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :param question: Текст питання, на яке потрібно знайти відповідь.
    :type question: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Текст відповіді на питання або повідомлення про помилку.
    :rtype: str
    """
    try:
        with open("faq.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        answer = data[lang].get(question, load_language_message(lang, 'faq_answer_not_found'))
        logger.debug(
            f"[REQ_ID:{correlation_id}] FAQ answer for '{question}' ({lang}): '{answer[:50]}...'"
        )
        return answer
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(
            f"ERR_UTIL_005 [REQ_ID:{correlation_id}]: Failed to load faq.json for lang '{lang}'. "
            f"Error: {e}", exc_info=True
        )
        return load_language_message(lang, 'data_load_error')
    except KeyError: # Якщо мова не знайдена в файлі FAQ
        logger.error(
            f"ERR_UTIL_006 [REQ_ID:{correlation_id}]: Language '{lang}' not found in faq.json."
        )
        return load_language_message(lang, 'data_load_error')


def get_court_info(lang: str, correlation_id: str = "N/A") -> dict:
    """
    Отримує інформацію про суд з файлу court_info.json для обраної мови.

    Читає контактну та загальну інформацію про судову установу з `court_info.json`.
    Якщо файл пошкоджений або інформація недоступна, повертає словник з
    повідомленнями про недоступність.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Словник з інформацією про суд (адреса, графік, телефон, email).
    :rtype: dict
    """
    try:
        with open("court_info.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        logger.debug(f"[REQ_ID:{correlation_id}] Loaded court info for language '{lang}'.")
        return data[lang]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(
            f"ERR_UTIL_007 [REQ_ID:{correlation_id}]: Failed to load court_info.json for lang '{lang}'. "
            f"Error: {e}", exc_info=True
        )
        return {
            "address": load_language_message(lang, 'info_not_available'),
            "work_time": load_language_message(lang, 'info_not_available'),
            "phone": load_language_message(lang, 'info_not_available'),
            "email": load_language_message(lang, 'info_not_available')
        }
    except KeyError:
        logger.error(
            f"ERR_UTIL_008 [REQ_ID:{correlation_id}]: Language '{lang}' not found in court_info.json."
        )
        return {
            "address": load_language_message(lang, 'info_not_available'),
            "work_time": load_language_message(lang, 'info_not_available'),
            "phone": load_language_message(lang, 'info_not_available'),
            "email": load_language_message(lang, 'info_not_available')
        }


def get_available_dates(correlation_id: str = "N/A") -> list:
    """
    Генерує список доступних дат для запису (будні дні протягом 14 днів).

    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Список доступних дат.
    :rtype: list[str]
    """
    logger.debug(f"[REQ_ID:{correlation_id}] Generating available dates.")
    today = datetime.now().date()
    dates = []
    for day_offset in range(14):
        current_date = today + timedelta(days=day_offset)
        if current_date.weekday() < 5:  # Понеділок (0) - П'ятниця (4)
            dates.append(str(current_date))
    return dates

def get_available_times_for_date(selected_date: str, correlation_id: str = "N/A") -> list:
    """
    Генерує список доступних часових слотів для вибраної дати.
    Виключає обідню перерву (13:00).

    :param selected_date: Вибрана дата у форматі Jamboree-MM-DD.
    :type selected_date: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Список доступних часових слотів у форматі "YYYY-MM-DD HH:MM".
    :rtype: list[str]
    """
    logger.debug(f"[REQ_ID:{correlation_id}] Generating available times for date: {selected_date}.")
    times = []
    for hour in range(9, 17):
        if hour == 13:
            continue
        times.append(f"{selected_date} {hour:02d}:00")
    return times

def save_appointment(user_id: int, name: str, time: str, correlation_id: str = "N/A"):
    """
    Зберігає інформацію про запис на консультацію до файлу appointments.json.

    Додає новий запис (user_id, ПІБ, дата та час) до існуючого списку записів.
    Якщо файл `appointments.json` не існує або пошкоджений, він буде створений
    або перевизначений.

    :param user_id: Унікальний ідентифікатор користувача Telegram.
    :type user_id: int
    :param name: Повне ім'я (ПІБ) користувача, який записується.
    :type name: str
    :param time: Вибраний час запису у форматі "YYYY-MM-DD HH:MM".
    :type time: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    """
    data = []
    try:
        if os.path.exists("appointments.json"):
            with open("appointments.json", "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
    except json.JSONDecodeError as e:
        logger.warning(
            f"WARN_UTIL_005 [REQ_ID:{correlation_id}]: appointments.json is corrupted for user {user_id}. "
            f"Resetting data. Error: {e}"
        )
    except FileNotFoundError:
        logger.info(
            f"[REQ_ID:{correlation_id}] appointments.json not found for user {user_id}. Creating new file."
        )
        pass

    data.append({"user_id": user_id, "name": name, "time": time})
    try:
        with open("appointments.json", "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)
        logger.info(
            f"[REQ_ID:{correlation_id}] Appointment saved for user {user_id}: {name} on {time}."
        )
    except IOError as e:
        logger.error(
            f"ERR_UTIL_009 [REQ_ID:{correlation_id}]: Failed to write to appointments.json "
            f"for user {user_id}. Error: {e}", exc_info=True
        )


def get_appointments_for_admin(correlation_id: str = "N/A") -> str:
    """
    Отримує відформатований список всіх записів для адміністратора.

    Читає всі записи з `appointments.json` та повертає їх у вигляді
    одного рядка, де кожен запис відображений на новому рядку.

    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Рядок з усіма записами або повідомлення про їх відсутність.
    :rtype: str
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not data:
            logger.info(f"[REQ_ID:{correlation_id}] No appointments found for admin request.")
            return load_language_message('uk', 'no_appointments_admin')
        logger.debug(f"[REQ_ID:{correlation_id}] Appointments data retrieved for admin.")
        return "\n".join([f"— {record['name']}, {record['time']}" for record in data])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(
            f"ERR_UTIL_010 [REQ_ID:{correlation_id}]: Failed to load appointments.json for admin. "
            f"Error: {e}", exc_info=True
        )
        return load_language_message('uk', 'data_load_error')

def get_appointments_for_user(correlation_id: str = "N/A") -> str:
    """
    Отримує відформатований список записів для конкретного користувача.

    (Ця функція була у вихідному коді, але наразі не використовується
    безпосередньо в обробниках бота для відображення користувачеві його власних записів.
    Повертає загальний список зайнятих часів, як у вихідному коді.)

    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Рядок з усіма зайнятими часами або повідомлення про їх відсутність.
    :rtype: str
    """
    try:
        with open("appointments.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        logger.debug(f"[REQ_ID:{correlation_id}] Appointments data retrieved for user (all).")
        # Тут можна було б додати фільтрацію по user_id
        return "\n".join([f"— {record['time']} ❌ Зайнято" for record in data])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(
            f"ERR_UTIL_011 [REQ_ID:{correlation_id}]: Failed to load appointments.json for user. "
            f"Error: {e}", exc_info=True
        )
        return load_language_message('uk', 'no_appointments_user')


async def send_admin_notification(bot_instance, message: str, user_info: dict = None):
    """
    Надсилає повідомлення про критичну помилку адміністраторам бота.
    Читає ID адміністраторів з файлу admins.json.

    :param bot_instance: Екземпляр бота (context.bot).
    :param message: Текст повідомлення для адміністратора.
    :type message: str
    :param user_info: Словник з інформацією про користувача (id, username, correlation_id).
                      Може бути None.
    :type user_info: dict
    """
    try:
        with open("admins.json", "r", encoding="utf-8") as file_handle:
            admins = json.load(file_handle)
        if not admins:
            logger.warning("WARN_UTIL_006: No admin IDs found in admins.json. Cannot send notification.")
            return

        admin_notification_text = load_language_message('uk', 'admin_critical_error_notification')

        # Додаємо контекстну інформацію про користувача, якщо вона надана
        context_info = ""
        if user_info:
            context_info += f"\nКористувач: {user_info.get('username', 'N/A')} ({user_info.get('user_id', 'N/A')})"
            context_info += f"\nREQ_ID: {user_info.get('correlation_id', 'N/A')}"
            context_info += f"\nПовідомлення користувачу: {user_info.get('user_friendly_message', 'N/A')}"

        full_message = f"{admin_notification_text}{context_info}\n\nДеталі помилки:\n{message}"

        for admin_id in admins:
            try:
                await bot_instance.send_message(chat_id=admin_id, text=full_message)
                logger.info(f"Sent critical error notification to admin {admin_id}.")
            except Exception as e:
                logger.error(f"ERR_UTIL_012: Failed to send notification to admin {admin_id}. Error: {e}", exc_info=True)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.critical(f"ERR_UTIL_013: Critical: Cannot load admins.json to send notification. Error: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"ERR_UTIL_014: Unexpected error in send_admin_notification: {e}", exc_info=True)

