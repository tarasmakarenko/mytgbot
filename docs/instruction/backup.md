
# Інструкції з резервного копіювання

Цей документ містить рекомендації щодо створення резервних копій (бекапів) даних та конфігураційних файлів **Telegram‑бота**. Регулярне резервне копіювання є критично важливим для відновлення системи у випадку збою або втрати даних.

## 1. Що підлягає резервному копіюванню

### Файли даних JSON

| Файл | Опис |
|------|------|
| `faq.json` | Поширені питання та відповіді |
| `court_info.json` | Інформація про суд |
| `court_schedule.json` | Розклад засідань |
| `contacts.json` | Контакти інших установ |
| `languages.json` | Налаштування мов користувачів |
| `appointments.json` | **Критичні** записи на консультації |
| `admins.json` | Список адміністраторів |

### Код проєкту

- Уся директорія проєкту `/opt/mytgbot/`  
  > Хоча код знаходиться у Git, локальний бекап пришвидшує відновлення після проблем із файловою системою сервера.

### Конфігураційні файли служби

- `/etc/systemd/system/telegram_bot.service`

---

## 2. Частота резервного копіювання

| Компонент | Рекомендована частота |
|-----------|-----------------------|
| **JSON‑файли** (особливо `appointments.json`) | Щоденно (або частіше) |
| **Код проєкту** | Щотижнево або після кожного релізу |
| **Конфігураційні файли** | Після кожної зміни |

---

## 3. Методи резервного копіювання

### 3.1. Ручне резервне копіювання

1. **Створити директорію для бекапів** (якщо її немає):

    ```bash
    sudo mkdir -p /var/backups/mytgbot_data
    sudo chown <username>:<username> /var/backups/mytgbot_data
    ```

2. **Бекап JSON‑файлів**:

    ```bash
    cd /opt/mytgbot/
    sudo tar -czvf /var/backups/mytgbot_data/json_data_$(date +%Y%m%d%H%M%S).tar.gz *.json
    ```

3. **Бекап коду проєкту** (без `.venv`, `_build`, `__pycache__`):

    ```bash
    sudo tar -czvf /var/backups/mytgbot_data/code_$(date +%Y%m%d%H%M%S).tar.gz /opt/mytgbot         --exclude='*.venv' --exclude='_build' --exclude='__pycache__'
    ```

4. **Бекап systemd‑файлу**:

    ```bash
    sudo cp /etc/systemd/system/telegram_bot.service /var/backups/mytgbot_data/
    ```

---

### 3.2. Автоматичне резервне копіювання (Cron)

1. **Створити скрипт** `/opt/mytgbot/backup_script.sh`:

    ```bash
    #!/bin/bash

    BACKUP_DIR="/var/backups/mytgbot_data"
    DATE=$(date +%Y%m%d%H%M%S)
    PROJECT_DIR="/opt/mytgbot"

    mkdir -p $BACKUP_DIR

    # JSON‑файли
    tar -czvf $BACKUP_DIR/json_data_${DATE}.tar.gz -C $PROJECT_DIR *.json

    # Код проєкту
    tar -czvf $BACKUP_DIR/code_${DATE}.tar.gz -C $PROJECT_DIR         --exclude='*.venv' --exclude='_build' --exclude='__pycache__' .

    # systemd‑unit
    cp /etc/systemd/system/telegram_bot.service $BACKUP_DIR/telegram_bot_service_${DATE}.service

    # Очистити старі бекапи (старші ніж 7 днів)
    find $BACKUP_DIR -type f -mtime +7 -name '*.gz' -delete
    find $BACKUP_DIR -type f -mtime +7 -name '*.service' -delete

    echo "Backup completed: ${DATE}"
    ```

2. **Зробити скрипт виконуваним**:

    ```bash
    sudo chmod +x /opt/mytgbot/backup_script.sh
    ```

3. **Додати cron‑завдання** (щодня о 02:00):

    ```bash
    sudo crontab -e
    ```

    Додати рядок:

    ```cron
    0 2 * * * /opt/mytgbot/backup_script.sh >> /var/log/mytgbot_backup.log 2>&1
    ```

---

## 4. Відновлення з резервної копії

1. **Зупинити бот**:

    ```bash
    sudo systemctl stop telegram_bot.service
    ```

2. **Перейти до директорії проєкту**:

    ```bash
    cd /opt/mytgbot/
    ```

3. **Очистити поточні JSON‑файли** (обережно!):

    ```bash
    sudo rm *.json
    ```

4. **Розпакувати останній бекап JSON‑файлів**:

    ```bash
    sudo tar -xzvf /var/backups/mytgbot_data/json_data_<LATEST_DATE>.tar.gz -C .
    ```

5. **(За потреби) Розпакувати бекап коду**:

    ```bash
    sudo tar -xzvf /var/backups/mytgbot_data/code_<LATEST_DATE>.tar.gz -C /opt/
    ```

6. **(За потреби) Відновити systemd‑unit**:

    ```bash
    sudo cp /var/backups/mytgbot_data/telegram_bot_service_<LATEST_DATE>.service         /etc/systemd/system/telegram_bot.service
    sudo systemctl daemon-reload
    ```

7. **Запустити бот**:

    ```bash
    sudo systemctl start telegram_bot.service
    ```

8. **Перевірити працездатність**:

    ```bash
    sudo systemctl status telegram_bot.service
    ```

> **Порада:** регулярно перевіряйте відновлення на тестовому сервері, щоб переконатися, що бекапи придатні до використання.
