"""
Модуль для обробки команд та повідомлень користувача в Telegram-боті.

Містить функції-обробники для різних сценаріїв взаємодії,
таких як запуск бота, вибір мови, відображення інформації,
а також багатоетапний діалог для запису на консультацію.
"""
import json
import logging
from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)
from for_test.utils import (
    load_language, set_language, get_faq_answer, get_court_info,
    get_available_dates, get_available_times_for_date,
    save_appointment, send_admin_notification, load_language_message, is_admin # Додано load_language_message, is_admin
)
from for_test.keyboards import (
    get_main_menu, get_language_keyboard, get_faq_keyboard, get_inline_keyboard
)

# Створюємо логер для цього модуля
logger = logging.getLogger(__name__)

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
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    logger.info(f"User {username} ({user_id}) started the dialog. Context: {context.user_data}")
    try:
        await update.message.reply_text(
            load_language_message('uk', 'choose_language'), reply_markup=get_language_keyboard()
        )
    except Exception as e:
        logger.error(f"ERR_HANDLER_001: Failed to send start message to user {user_id}: {e}", exc_info=True)
        # Сповіщення користувача про загальну помилку
        await update.message.reply_text(
            load_language_message('uk', 'generic_user_error')
        )
        # Сповіщення адміністратора про критичну помилку
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_001 при запуску діалогу для {user_id}. {e}"
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
    username = update.effective_user.username or update.effective_user.first_name
    try:
        set_language(user_id, lang)
        logger.info(f"User {username} ({user_id}) set language to '{lang}'.")
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            load_language_message(lang, 'language_set_success'), reply_markup=get_main_menu(lang)
        )
    except Exception as e:
        logger.error(f"ERR_HANDLER_002: Error setting language for user {user_id}: {e}", exc_info=True)
        await update.callback_query.message.reply_text(
            load_language_message(lang, 'generic_user_error_with_contact')
        )
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_002 при встановленні мови для {user_id}. {e}"
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
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.debug(f"User {user_id} requested FAQ. Lang: {lang}")
    try:
        await update.message.reply_text(load_language_message(lang, 'choose_faq_question'),
                                        reply_markup=get_faq_keyboard(lang))
    except Exception as e:
        logger.error(f"ERR_HANDLER_003: Error showing FAQ for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_003 при відображенні FAQ для {user_id}. {e}"
        )

async def answer_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання відповіді на вибране питання з FAQ.

    Отримує текст питання, знаходить відповідь у базі знань
    (faq.json) та відправляє її користувачеві.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення (повідомлення).
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    question = update.message.text
    logger.debug(f"User {user_id} asked: '{question}'. Lang: {lang}")
    try:
        answer = get_faq_answer(lang, question)
        if "⚠️" in answer: # Простий спосіб виявити, що відповіді не знайдено
            logger.warning(f"WARN_HANDLER_001: No FAQ answer found for user {user_id} for question: '{question}'.")
        await update.message.reply_text(answer, reply_markup=get_main_menu(lang))
    except Exception as e:
        logger.error(f"ERR_HANDLER_004: Error answering FAQ for user {user_id} for question '{question}': {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_004 при відповіді на FAQ для {user_id}. {e}"
        )

async def show_court_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання інформації про судову установу.

    Відправляє користувачеві контактну та загальну інформацію про суд
    (адреса, графік роботи, телефон, email) відповідно до обраної мови.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.debug(f"User {user_id} requested court info. Lang: {lang}")
    try:
        info = get_court_info(lang)
        text = (
            f"📍 {load_language_message(lang, 'address')}: {info['address']}\n"
            f"🕒 {load_language_message(lang, 'schedule')}: {info['work_time']}\n"
            f"📞 {load_language_message(lang, 'phone')}: {info['phone']}\n"
            f"✉️ {load_language_message(lang, 'email')}: {info['email']}"
        )
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"ERR_HANDLER_005: Error showing court info for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_005 при відображенні інфо про суд для {user_id}. {e}"
        )

async def show_court_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для відображення розкладу судових засідань.

    Завантажує інформацію про розклад з court_schedule.json
    та відправляє її користувачеві у структурованому вигляді.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.debug(f"User {user_id} requested court schedule. Lang: {lang}")
    try:
        with open("court_schedule.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not data:
            msg = load_language_message(lang, 'no_schedule_available')
            logger.info(f"User {user_id}: No schedule data found.")
        else:
            msg = load_language_message(lang, 'court_schedule_title') + "\n"
            for item in data:
                msg += (
                    f"{item['date']} – {load_language_message(lang, 'case')}"
                    f" {item['case']}: {item['time']},"
                    f" {load_language_message(lang, 'judge')} {item['judge']}\n"
                )
        await update.message.reply_text(msg)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"ERR_HANDLER_006: Error loading court schedule for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'data_load_error'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_006 при завантаженні розкладу суду для {user_id}. {e}"
        )
    except Exception as e:
        logger.error(f"ERR_HANDLER_007: Unexpected error in show_court_schedule for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_007 при відображенні розкладу суду для {user_id}. {e}"
        )

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для надання контактної інформації інших установ.

    Завантажує контактну інформацію з contacts.json
    та відправляє її користувачеві відповідно до обраної мови.

    :param update: Об'єкт, що містить інформацію про вхідне оновлення.
    :type update: telegram.Update
    :param context: Об'єкт контексту для поточного оновлення.
    :type context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.debug(f"User {user_id} requested other contacts. Lang: {lang}")
    try:
        with open("contacts.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        entries = data.get(lang, [])
        if not entries:
            msg = load_language_message(lang, 'no_contacts_available')
            logger.info(f"User {user_id}: No contacts data found for lang {lang}.")
        else:
            msg = load_language_message(lang, 'other_contacts_title') + "\n"
            for contact in entries:
                msg += f"📌 {contact['org']} — {contact['phone']}\n"
        await update.message.reply_text(msg)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"ERR_HANDLER_008: Error loading other contacts for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'data_load_error'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_008 при завантаженні контактів для {user_id}. {e}"
        )
    except Exception as e:
        logger.error(f"ERR_HANDLER_009: Unexpected error in show_contacts for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_009 при відображенні контактів для {user_id}. {e}"
        )

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
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.info(f"User {user_id} started appointment booking.")
    try:
        await update.message.reply_text(load_language_message(lang, 'enter_full_name'))
    except Exception as e:
        logger.error(f"ERR_HANDLER_010: Error asking name for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_010 при запиті ПІБ для {user_id}. {e}"
        )
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
    user_id = update.effective_user.id
    lang = load_language(user_id)
    try:
        context.user_data["name"] = update.message.text
        logger.debug(f"User {user_id} entered name: {context.user_data['name']}")
        dates = get_available_dates()
        if not dates:
            logger.warning(f"WARN_HANDLER_002: No available dates generated for user {user_id}.")
            await update.message.reply_text(load_language_message(lang, 'no_dates_available'))
            return ConversationHandler.END # Завершуємо діалог, бо немає дат
        await update.message.reply_text(load_language_message(lang, 'choose_date'), reply_markup=get_inline_keyboard(dates))
    except Exception as e:
        logger.error(f"ERR_HANDLER_011: Error asking date for user {user_id} after name input: {e}", exc_info=True)
        await update.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_011 при запиті дати для {user_id}. {e}"
        )
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
    user_id = update.effective_user.id
    lang = load_language(user_id)
    try:
        selected_date = update.callback_query.data
        context.user_data["selected_date"] = selected_date
        logger.debug(f"User {user_id} selected date: {selected_date}")
        times = get_available_times_for_date(selected_date)
        if not times:
            logger.warning(f"WARN_HANDLER_003: No available times generated for user {user_id} on {selected_date}.")
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(load_language_message(lang, 'no_times_available'))
            return ConversationHandler.END # Завершуємо діалог
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(load_language_message(lang, 'choose_time'), reply_markup=get_inline_keyboard(times))
    except Exception as e:
        logger.error(f"ERR_HANDLER_012: Error asking time for user {user_id} after date input: {e}", exc_info=True)
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_012 при запиті часу для {user_id}. {e}"
        )
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
    try:
        time = update.callback_query.data
        name = context.user_data.get("name", load_language_message(lang, 'no_name_provided'))

        # Перевірка на вже існуючий запис (базова)
        # У продакшені варто додати більш надійну перевірку у utils
        appointments_exist = False # Заглушка, для реальної перевірки потрібен доступ до appointments.json
        # if appointments_exist:
        #    logger.warning(f"WARN_HANDLER_004: User {user_id} attempted to book already taken slot: {time}")
        #    await update.callback_query.message.reply_text(load_language_message(lang, 'slot_already_taken'))
        #    return ConversationHandler.END

        save_appointment(user_id, name, time)
        logger.info(f"User {user_id} successfully booked appointment: {name} on {time}.")
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            load_language_message(lang, 'appointment_booked_success'), reply_markup=get_main_menu(lang)
        )
    except Exception as e:
        logger.error(f"ERR_HANDLER_013: Error confirming appointment for user {user_id}: {e}", exc_info=True)
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(load_language_message(lang, 'generic_user_error_with_contact'))
        await send_admin_notification(
            context.bot, f"Критична помилка ERR_HANDLER_013 при підтвердженні запису для {user_id}. {e}"
        )
    return ConversationHandler.END

# Обробник для непередбачених текстових повідомлень, що не відповідають жодному шаблону
async def fallback_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для повідомлень, що не були розпізнані.

    Надсилає користувачеві повідомлення про те, що команда не розпізнана.
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    logger.info(f"User {user_id} sent unrecognized message: '{update.message.text}'")
    await update.message.reply_text(load_language_message(lang, 'unrecognized_command'), reply_markup=get_main_menu(lang))


# Обробник для адмінських команд (лише для прикладу, не повний функціонал)
async def admin_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник для адмінських команд.

    Тільки адміни можуть використовувати цю команду.
    """
    user_id = update.effective_user.id
    lang = load_language(user_id)
    if is_admin(user_id):
        logger.info(f"Admin {user_id} used admin command.")
        await update.message.reply_text(load_language_message(lang, 'admin_panel_greeting'))
    else:
        logger.warning(f"Unauthorized access attempt to admin command by user {user_id}.")
        await update.message.reply_text(load_language_message(lang, 'unauthorized_access'))


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
        fallbacks=[
            # Цей fallback обробник буде викликаний, якщо користувач відправить щось не очікуване
            # в середині діалогу або для завершення діалогу
            MessageHandler(filters.TEXT | filters.COMMAND, fallback_message_handler),
            CallbackQueryHandler(fallback_message_handler) # Для невідомих callback_query
        ]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command_handler)) # Додаємо адмінську команду
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
    # Обробник для будь-яких інших текстових повідомлень, що не були оброблені
    # Розміщується останнім, щоб не перехоплювати інші команди
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message_handler))

