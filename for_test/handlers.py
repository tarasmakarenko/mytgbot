"""
Модуль для обробки команд та повідомлень користувача в Telegram-боті.
Містить функції-обробники для різних сценаріїв взаємодії.
"""
import json
from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
from utils import (
    load_language, set_language, get_faq_answer, get_court_info,
    get_available_dates, get_available_times_for_date,
    save_appointment
)
from keyboards import (
    get_main_menu, get_language_keyboard, get_faq_keyboard, get_inline_keyboard
)

# Визначення станів для ConversationHandler
LANG_SELECT, ASK_NAME, ASK_DATE, ASK_TIME = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробник команди /start.
    Пропонує користувачеві обрати мову інтерфейсу.
    """
    await update.message.reply_text(
        "🌐 Оберіть мову / Choose language:", reply_markup=get_language_keyboard()
    )
    return LANG_SELECT

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробник вибору мови.
    Зберігає обрану мову та відображає головне меню.
    """
    lang = update.callback_query.data
    user_id = update.effective_user.id
    set_language(user_id, lang)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "✅ Мову встановлено!", reply_markup=get_main_menu(lang)
    )
    return ConversationHandler.END

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробник для показу списку поширених питань (FAQ).
    """
    lang = load_language(update.effective_user.id)
    await update.message.reply_text("❓ Оберіть питання:", reply_markup=get_faq_keyboard(lang))

async def answer_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробник для надання відповіді на вибране питання з FAQ.
    """
    lang = load_language(update.effective_user.id)
    question = update.message.text
    answer = get_faq_answer(lang, question)
    await update.message.reply_text(answer, reply_markup=get_main_menu(lang))

async def show_court_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробник для надання інформації про судову установу.
    """
    lang = load_language(update.effective_user.id)
    info = get_court_info(lang)
    text = (
        f"📍 Адреса: {info['address']}\n"
        f"🕒 Графік: {info['work_time']}\n"
        f"📞 Телефон: {info['phone']}\n"
        f"✉️ Email: {info['email']}"
    )
    await update.message.reply_text(text)

async def show_court_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробник для відображення розкладу судових засідань.
    """
    with open("court_schedule.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    msg = "📅 Розклад засідань:\n"
    for item in data:
        msg += (
            f"{item['date']} – Справа {item['case']}: {item['time']},"
            f" Суддя {item['judge']}\n"
        )
    await update.message.reply_text(msg)

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробник для надання контактної інформації інших установ.
    """
    lang = load_language(update.effective_user.id)
    with open("contacts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get(lang, [])
    msg = "📞 Контакти інших установ:\n"
    for contact in entries:
        msg += f"📌 {contact['org']} — {contact['phone']}\n"
    await update.message.reply_text(msg)

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Початок діалогу запису на консультацію.
    Запитує ПІБ користувача.
    """
    await update.message.reply_text("📝 Введіть ПІБ для запису:")
    return ASK_NAME

async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Продовження діалогу запису.
    Зберігає ПІБ та пропонує доступні дати.
    """
    context.user_data["name"] = update.message.text
    dates = get_available_dates()
    await update.message.reply_text("📅 Оберіть дату:", reply_markup=get_inline_keyboard(dates))
    return ASK_DATE

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Продовження діалогу запису.
    Зберігає дату та пропонує доступні часові слоти.
    """
    selected_date = update.callback_query.data
    context.user_data["selected_date"] = selected_date
    times = get_available_times_for_date(selected_date)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("⏰ Оберіть час:", reply_markup=get_inline_keyboard(times))
    return ASK_TIME

async def confirm_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Завершення діалогу запису.
    Зберігає повну інформацію про запис та надсилає підтвердження.
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    time = update.callback_query.data
    name = context.user_data.get("name", "Без імені")
    save_appointment(user_id, name, time)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("✅ Ви успішно записані!", reply_markup=get_main_menu(lang))
    return ConversationHandler.END

def register_handlers(app):
    """
    Реєструє всі обробники в Telegram Application.
    """
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(📝|📅) Запис"), ask_name)],
        states={
            LANG_SELECT: [CallbackQueryHandler(language_selected)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)],
            ASK_DATE: [CallbackQueryHandler(ask_time)],
            ASK_TIME: [CallbackQueryHandler(confirm_time)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^(uk|en)$"))
    app.add_handler(MessageHandler(filters.Regex("^(❓ FAQ|❓ Поширені питання)$"), show_faq))
    # Використовуємо filters.Regex для виявлення питання та уникаємо "unreachable code"
    app.add_handler(MessageHandler(filters.Regex(r"^(Як|How).*$"), answer_faq))
    app.add_handler(MessageHandler(filters.Regex("^(ℹ️|📍)"), show_court_info))
    app.add_handler(MessageHandler(filters.Regex("^(🗓 Календар засідань|🗓 Hearing Calendar)$"), show_court_schedule))
    app.add_handler(MessageHandler(filters.Regex("^(📞 Контакти інших установ|📞 Other Institutions)$"), show_contacts))

