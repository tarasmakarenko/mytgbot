from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import json

def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Українська", callback_data="uk"),
         InlineKeyboardButton("English", callback_data="en")]
    ])

def get_main_menu(lang):
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

def get_faq_keyboard(lang):
    with open("faq.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return ReplyKeyboardMarkup([[q] for q in data[lang].keys()], resize_keyboard=True)

def get_inline_keyboard(options):
    return InlineKeyboardMarkup([[InlineKeyboardButton(opt, callback_data=opt)] for opt in options])
