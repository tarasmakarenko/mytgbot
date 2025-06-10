"""
Модуль для генерації кастомних клавіатур для Telegram-бота.
"""
import json # Стандартна бібліотека
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton # Стороння бібліотека

def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Генерує інлайн-клавіатуру для вибору мови.
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Українська", callback_data="uk"),
         InlineKeyboardButton("English", callback_data="en")]
    ])

def get_main_menu(lang: str) -> ReplyKeyboardMarkup:
    """
    Генерує клавіатуру головного меню відповідно до обраної мови.
    """
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

def get_faq_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    Генерує клавіатуру з поширеними питаннями для обраної мови.
    """
    with open("faq.json", "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    return ReplyKeyboardMarkup([[q] for q in data[lang].keys()], resize_keyboard=True)

def get_inline_keyboard(options: list) -> InlineKeyboardMarkup:
    """
    Генерує інлайн-клавіатуру з динамічним списком опцій.
    """
    return InlineKeyboardMarkup([[InlineKeyboardButton(opt, callback_data=opt)] for opt in options])
# Додано фінальний порожній рядок
