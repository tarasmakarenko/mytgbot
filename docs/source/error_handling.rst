
# Логування та обробка помилок

Цей документ описує стратегії **логування** та **обробки помилок**, реалізовані в проєкті Telegram‑бота, які допомагають діагностувати та вирішувати проблеми як під час розробки, так і у production‑середовищі.

## 1. Система логування

Проєкт використовує вбудовану бібліотеку **`logging`** із Python.

### 1.1. Рівні логування

| Рівень | Призначення |
|--------|-------------|
| **DEBUG** | Детальна діагностика, трасування коду |
| **INFO** | Підтвердження успішних операцій |
| **WARNING** | Потенційні проблеми, що не блокують роботу |
| **ERROR** | Серйозні збої окремих функцій |
| **CRITICAL** | Критичні помилки, що загрожують роботі застосунку |

### 1.2. Конфігурація логування (`bot.py`)

- **Мінімальний рівень** визначається змінною середовища `LOG_LEVEL`.  
  Якщо змінна не встановлена — використовується `INFO`.

```powershell
# Windows (PowerShell)
$env:LOG_LEVEL="DEBUG"
python for_test/bot.py
```

```bash
# Linux/macOS
export LOG_LEVEL="DEBUG"
python for_test/bot.py
```

- **Handlers**:

  | Обробник | Опис |
  |----------|------|
  | `StreamHandler` | Вивід у консоль (journalctl у prod) |
  | `RotatingFileHandler` | Файл `bot.log` з ротацією <br>`maxBytes = 5 MB`, `backupCount = 5`, `encoding = utf‑8` |

- **Формат**:  
  `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### 1.3. Контекстна інформація

- `user_id`, `username`
- Параметри операцій
- Унікальні коди помилок: `ERR_UTIL_001`, `ERR_HANDLER_005`, …

---

## 2. Обробка помилок

### 2.1. Перехоплення винятків

- **`try‑except`** з конкретними винятками (`FileNotFoundError`, `JSONDecodeError`, …).
- Логування з `logger.error(..., exc_info=True)` для повного _stack trace_.

### 2.2. Повідомлення користувачам

- Централізований файл **`messages.json`** для локалізації.
- При помилці — загальне повідомлення без технічних деталей.  
  > “Вибачте, сталася неочікувана помилка. Спробуйте пізніше.”

### 2.3. Сповіщення адміністратора

- Функція `send_admin_notification()` у `utils.py`.
- При помилках рівня **ERROR/CRITICAL** надсилає трасування стека адміністраторам із `admins.json`.

---

## 3. Конфігурація та приклади

### 3.1. Зміна `LOG_LEVEL`

| OS | Приклад |
|----|---------|
| Windows | `$env:LOG_LEVEL="INFO"` |
| Linux/macOS | `export LOG_LEVEL="INFO"` |

### 3.2. Приклад фрагмента `bot.log`

```text
2025-06-12 10:30:00,123 - __main__ - INFO - ✅ Бот запущено!
2025-06-12 10:30:20,300 - utils - WARNING - WARN_UTIL_002: Failed to load languages.json ...
2025-06-12 10:30:25,400 - utils - ERROR - ERR_UTIL_005: Failed to load faq.json ...
Traceback (most recent call last):
  ...
```

### 3.3. Приклади локалізованих повідомлень

| Ключ | UA | EN |
|------|----|----|
| `generic_error` | “Вибачте, сталася неочікувана помилка…” | “Sorry, an unexpected error occurred…” |
| `faq_not_found` | “⚠️ Вибачте, відповіді не знайдено.” | — |

---

## Висновок

Реалізована система логування з ротацією файлів, гнучкими рівнями та контекстною інформацією, а також **обробка винятків** із повідомленнями користувачам і сповіщенням адміністраторів. Це підвищує надійність і спрощує підтримку Telegram‑бота.
