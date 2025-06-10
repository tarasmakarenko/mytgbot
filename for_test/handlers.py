"""
Модуль для обробки команд та повідомлень користувача в Telegram-боті.

Містить функції-обробники для різних сценаріїв взаємодії,
таких як запуск бота, вибір мови, відображення інформації,
а також багатоетапний діалог для запису на консультацію.
"""
import json # Стандартна бібліотека

from telegram import Update # Стороння бібліотека
from telegram.ext import ( # Стороння бібліотека
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
from utils import ( # Локальний модуль
    load_language, set_language, get_faq_answer, get_court_info,
    get_available_dates, get_available_times_for_date,
    save_appointment
)
from keyboards import ( # Локальний модуль
    get_main_menu, get_language_keyboard, get_faq_keyboard, get_inline_keyboard
)

# Визначення станів для ConversationHandler
LANG_SELECT, ASK_NAME, ASK_DATE, ASK_TIME = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробник команди /start.

    Надсилає вітальне повідомлення та пропонує користувачеві обрати мову інтерфейсу
    за допомогою інлайн-клавіатури. Це початкова точка входу в бота.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (повідомлення).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан для ConversationHandler.
    :rtype: int
    """
    await update.message.reply_text(
        "🌐 Оберіть мову / Choose language:", reply_markup=get_language_keyboard()
    )
    return LANG_SELECT

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробник вибору мови.

    Зберігає обрану мову користувача (українську або англійську)
    та відображає головне меню бота відповідно до цього вибору.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (callback_query).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан для ConversationHandler, завершуючи вибір мови.
    :rtype: int
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
    """Обробник для показу списку поширених питань (FAQ).

    Відправляє користувачеві клавіатуру з доступними питаннями FAQ
    відповідно до обраної мови.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    lang = load_language(update.effective_user.id)
    await update.message.reply_text("❓ Оберіть питання:", reply_markup=get_faq_keyboard(lang))

async def answer_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання відповіді на вибране питання з FAQ.

    Отримує текст питання, знаходить відповідь у базі знань
    (faq.json) та відправляє її користувачеві.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (повідомлення).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    lang = load_language(update.effective_user.id)
    question = update.message.text
    answer = get_faq_answer(lang, question)
    await update.message.reply_text(answer, reply_markup=get_main_menu(lang))

async def show_court_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання інформації про судову установу.

    Відправляє користувачеві контактну та загальну інформацію про суд
    (адреса, графік роботи, телефон, email) відповідно до обраної мови.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
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
    """Обробник для відображення розкладу судових засідань.

    Завантажує інформацію про розклад з court_schedule.json
    та відправляє її користувачеві у структурованому вигляді.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    with open("court_schedule.json", "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    msg = "📅 Розклад засідань:\n"
    for item in data:
        msg += (
            f"{item['date']} – Справа {item['case']}: {item['time']},"
            f" Суддя {item['judge']}\n"
        )
    await update.message.reply_text(msg)

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання контактної інформації інших установ.

    Завантажує контактну інформацію з contacts.json
    та відправляє її користувачеві відповідно до обраної мови.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    lang = load_language(update.effective_user.id)
    with open("contacts.json", "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    entries = data.get(lang, [])
    msg = "📞 Контакти інших установ:\n"
    for contact in entries:
        msg += f"📌 {contact['org']} — {contact['phone']}\n"
    await update.message.reply_text(msg)

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок діалогу запису на консультацію.

    Запитує у користувача його ПІБ для подальшого запису.
    Переводить діалог у стан ASK_NAME.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (повідомлення).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан діалогу.
    :rtype: int
    """
    await update.message.reply_text("📝 Введіть ПІБ для запису:")
    return ASK_NAME

async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Продовження діалогу запису на консультацію.

    Зберігає введене користувачем ПІБ та пропонує доступні дати
    для запису за допомогою інлайн-клавіатури. Переводить діалог у стан ASK_DATE.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (повідомлення з ПІБ).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення, зберігає user_data.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан діалогу.
    :rtype: int
    """
    context.user_data["name"] = update.message.text
    dates = get_available_dates()
    await update.message.reply_text("📅 Оберіть дату:", reply_markup=get_inline_keyboard(dates))
    return ASK_DATE

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Продовження діалогу запису на консультацію.

    Зберігає обрану дату та пропонує доступні часові слоти
    для цієї дати за допомогою інлайн-клавіатури. Переводить діалог у стан ASK_TIME.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (callback_query з датою).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення, зберігає user_data.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан діалогу.
    :rtype: int
    """
    selected_date = update.callback_query.data
    context.user_data["selected_date"] = selected_date
    times = get_available_times_for_date(selected_date)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("⏰ Оберіть час:", reply_markup=get_inline_keyboard(times))
    return ASK_TIME

async def confirm_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершення діалогу запису на консультацію.

    Зберігає повну інформацію про запис (ПІБ, дату, час) у appointments.json
    та надсилає користувачеві підтвердження успішного запису. Завершує діалог.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (callback_query з часом).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення, містить user_data.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    :returns: Наступний стан діалогу, що сигналізує про його завершення.
    :rtype: int
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
    """Реєструє всі обробники в об'єкті Telegram Application.

    Ця функція додає CommandHandler для команди /start, ConversationHandler
    для багатоетапного діалогу запису на консультацію, а також MessageHandler
    та CallbackQueryHandler для обробки інших типів повідомлень та натискань кнопок.

    :param app: Об'єкт Application, до якого реєструються обробники.
    :type app: telegram.ext.Application
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
    app.add_handler(MessageHandler(filters.Regex(r"^(Як|How).*"), answer_faq))
    app.add_handler(MessageHandler(filters.Regex("^(ℹ️|📍)"), show_court_info))
    app.add_handler(MessageHandler(
        filters.Regex("^(🗓 Календар засідань|🗓 Hearing Calendar)$"),
        show_court_schedule
    ))
    app.add_handler(MessageHandler(
        filters.Regex("^(📞 Контакти інших установ|📞 Other Institutions)$"),
        show_contacts
    ))
