
# Інструкції з розгортання у виробничому середовищі

Цей документ містить покрокові інструкції для інженерів з розгортання та DevOps фахівців щодо підготовки середовища та розгортання Telegram-бота у виробничому (production) середовищі.

## 1. Вимоги до апаратного забезпечення

Проєкт Telegram-бота має відносно низькі вимоги до апаратних ресурсів, оскільки він не обробляє великі обсяги даних у реальному часі та не вимагає інтенсивних обчислень.

- **Архітектура:** x86-64 (сумісний з більшістю хмарних провайдерів та фізичних серверів).
- **Мінімальні вимоги до CPU:** 1 vCPU (віртуальний процесор) або 1 ядро.
- **Мінімальні вимоги до пам'яті (RAM):** 512 MB – 1 GB.
- **Мінімальні вимоги до дискового простору:** 2 GB (для ОС, залежностей Python та файлів даних бота).

## 2. Необхідне програмне забезпечення

Переконайтеся, що на сервері встановлено наступне програмне забезпечення:

- **Операційна система:** Ubuntu Server 20.04 LTS або новіша, Debian 11+. Альтернативи: CentOS 7/8+, RHEL.
- **Python 3.9+:** Встановіть Python та pip. Рекомендовано використовувати `pyenv` або `conda`, або ж встановити системно:

```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

- **Git:**

```bash
sudo apt install git
```

- **venv:** Для створення віртуальних середовищ.
- **systemd:** Для створення служби бота.
- **supervisor (опціонально):** Для моніторингу та перезапуску бота.

## 3. Налаштування мережі

- **Outbound Access:** Потрібен порт 443 для доступу до `api.telegram.org`.
- **Inbound Access:** Відкрийте порт 22 для SSH-доступу.

## 4. Конфігурація серверів та розгортання коду

**Клонування репозиторію:**

```bash
cd /opt/
sudo git clone https://github.com/tarasmakarenko/mytgbot.git
sudo chown -R <username>:<username> mytgbot
cd mytgbot
```

**Налаштування віртуального середовища:**

```bash
python3.9 -m venv .venv
source .venv/bin/activate
```

**Встановлення залежностей:**

```bash
pip install -r requirements.txt
```

**Налаштування токена бота:**

- Замініть токен у `for_test/bot.py`.
- Краще використовувати змінні середовища:

```python
BOT_TOKEN = os.environ.get('BOT_TOKEN')
```

**Налаштування JSON-файлів:**

Переконайтесь, що файли на місці або скопіюйте їх з бекапу:

```bash
sudo cp /path/to/your/backup/*.json .
```

## 5. Створення служби systemd

**Файл /etc/systemd/system/telegram_bot.service:**

```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
User=<username>
Group=<username>
WorkingDirectory=/opt/mytgbot/
Environment="BOT_TOKEN=YOUR_REAL_BOT_TOKEN_HERE"
ExecStart=/opt/mytgbot/.venv/bin/python /opt/mytgbot/for_test/bot.py
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

**Увімкнення служби:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram_bot.service
sudo systemctl start telegram_bot.service
```

## 6. Перевірка працездатності

**Перевірка статусу:**

```bash
sudo systemctl status telegram_bot.service
```

**Логи:**

```bash
sudo journalctl -u telegram_bot.service -f
```

**Тестування бота в Telegram:**

- Надішліть `/start`.
- Перевірте всі основні функції (FAQ, суд, консультації).

