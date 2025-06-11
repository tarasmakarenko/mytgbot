"""
Модуль для генерації кастомних клавіатур для Telegram-бота.

Містить функції для створення інлайн-клавіатур та клавіатур головного меню,
що використовуються для взаємодії з користувачем.
"""
import json
import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Створюємо логер для цього модуля
logger = logging.getLogger(__name__)

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Генерує інлайн-клавіатуру для вибору мови.

    Клавіатура містить дві кнопки: "Українська" та "English",
    кожна з відповідним callback_data.

    :returns: Об'єкт InlineKeyboardMarkup для вибору мови.
    :rtype: telegram.InlineKeyboardMarkup
    """
    logger.debug("Generating language selection keyboard.")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Українська", callback_data="uk"),
         InlineKeyboardButton("English", callback_data="en")]
    ])

def get_main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Генерує клавіатуру головного меню відповідно до обраної мови.

    Повертає ReplyKeyboardMarkup з основними опціями меню
    (FAQ, Запис на консультацію, Інформація про суд, Календар засідань, Контакти)
    українською або англійською мовами. Клавіатура автоматично змінює розмір.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :returns: Об'єкт ReplyKeyboardMarkup для головного меню.
    :rtype: telegram.ReplyKeyboardMarkup
    """
    logger.debug(f"Generating main menu keyboard for language '{lang}'.")
    if lang == "en":
        return ReplyKeyboardMarkup(
            [["❓ FAQ", "📅 Appointment"],
             ["ℹ️ Court Info", "🗓 Hearing Calendar"],
             ["📞 Other Institutions"]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        [["❓ Поширені питання", "📅 Запис на консультацію"],
         ["ℹ️ Інформація про суд", "🗓 Календар засідань"],
         ["📞 Контакти інших установ"]],
        resize_keyboard=True
    )

def get_faq_keyboard(lang: str, correlation_id: str = "N/A") -> ReplyKeyboardMarkup:
    """Генерує клавіатуру з поширеними питаннями для обраної мови.

    Читає питання з файлу `faq.json` та створює ReplyKeyboardMarkup,
    де кожне питання є окремою кнопкою.

    :param lang: Код мови ('uk' або 'en').
    :type lang: str
    :param correlation_id: Унікальний ідентифікатор запиту для трасування.
    :type correlation_id: str
    :returns: Об'єкт ReplyKeyboardMarkup зі списком питань FAQ.
    :rtype: telegram.ReplyKeyboardMarkup
    """
    logger.debug(f"[REQ_ID:{correlation_id}] Generating FAQ keyboard for language '{lang}'.")
    try:
        with open("faq.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return ReplyKeyboardMarkup([[q] for q in data[lang].keys()], resize_keyboard=True)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"ERR_KB_001 [REQ_ID:{correlation_id}]: Failed to load faq.json for language '{lang}': {e}", exc_info=True)
        # У випадку помилки, повертаємо порожню клавіатуру або меню за замовчуванням
        return ReplyKeyboardMarkup([["Помилка завантаження FAQ"]], resize_keyboard=True)

def get_inline_keyboard(options: list) -> InlineKeyboardMarkup:
    """Генерує інлайн-клавіатуру з динамічним списком опцій.

    Створює InlineKeyboardMarkup, де кожна опція зі списку
    стає окремою кнопкою з її текстом як `callback_data`.

    :param options: Список рядків, які будуть використані як текст кнопок та callback_data.
    :type options: list[str]
    :returns: Об'єкт InlineKeyboardMarkup з динамічними опціями.
    :rtype: telegram.InlineKeyboardMarkup
    """
    logger.debug(f"Generating inline keyboard with {len(options)} options.")
    return InlineKeyboardMarkup([[InlineKeyboardButton(opt, callback_data=opt)] for opt in options])

