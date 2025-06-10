Інструкція з генерації документації проєкту
Цей документ містить покрокову інструкцію для встановлення необхідних інструментів, налаштування Sphinx та генерації HTML-документації для проєкту Telegram-бота.

1. Встановлення необхідних інструментів
Для генерації документації вам потрібно встановити Sphinx та тему оформлення "Read the Docs".

Активуйте віртуальне середовище:
Перейдіть до кореневої директорії вашого проєкту в терміналі та активуйте віртуальне середовище:

# Для Windows
.\.venv\Scripts\activate

# Для Linux/macOS
source ./.venv/bin/activate

Встановіть Sphinx та тему:

pip install sphinx sphinx-rtd-theme

2. Ініціалізація проєкту Sphinx (Виконується один раз)
Якщо проєкт Sphinx ще не ініціалізовано, виконайте наступну команду в кореневій директорії вашого проєкту:

sphinx-quickstart docs

Під час інтерактивного процесу:

Separate source and build directories (y/n): n

Project name: Telegram Bot для Судових Установ

Author name(s): Ваше Ім'я

Project language [en]: uk
Для інших питань можна використовувати значення за замовчуванням.

3. Налаштування файлу конфігурації conf.py
Відкрийте файл docs/conf.py (розташований у папці docs) та внесіть наступні зміни:

Додайте шлях до вашого проєкту:
Знайдіть блок import os та import sys та додайте (або розкоментуйте та модифікуйте):

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

Увімкніть необхідні розширення:
Знайдіть змінну extensions та додайте (або переконайтеся, що вони є):

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', # Для підтримки Google/NumPy style docstrings (не обов'язково, але корисно)
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
]

Встановіть тему оформлення:
Знайдіть змінну html_theme та встановіть:

html_theme = 'sphinx_rtd_theme'

Увімкніть відображення todo-нотаток:
Додайте або змініть:

todo_include_todos = True

Переконайтеся, що мова встановлена на українську:
Знайдіть змінну language та встановіть:

language = 'uk'

4. Створення .rst файлів для ваших модулів
У папці docs створіть файли для кожного модуля вашого бота. Ці файли вказують Sphinx, які модулі аналізувати за допомогою autodoc.

docs/modules.rst:

Модулі Telegram-бота
===================

.. toctree::
   :maxdepth: 2
   :caption: Зміст:

   bot
   handlers
   keyboards
   utils

docs/bot.rst:

Модуль Bot
==========

.. automodule:: bot
   :members:
   :undoc-members:
   :show-inheritance:

docs/handlers.rst:

Модуль Handlers
===============

.. automodule:: handlers
   :members:
   :undoc-members:
   :show-inheritance:

docs/keyboards.rst:

Модуль Keyboards
================

.. automodule:: keyboards
   :members:
   :undoc-members:
   :show-inheritance:

docs/utils.rst:

Модуль Utils
============

.. automodule:: utils
   :members:
   :undoc-members:
   :show-inheritance:

Обов'язково додайте modules.rst до вашого головного файлу docs/index.rst. Відкрийте docs/index.rst та додайте modules до секції .. toctree:::

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   # ... інші ваші файли

5. Генерація документації
Після виконання всіх попередніх кроків, перейдіть до папки docs у терміналі (саме туди, де знаходяться Makefile та make.bat).

Виконайте команду для збірки HTML-документації:

make html

Або для Windows, якщо make не працює:

.\make.bat html

Згенеровані HTML-файли будуть знаходитися в папці docs/_build/html. Ви можете відкрити docs/_build/html/index.html у вашому веб-браузері для перегляду документації. Переконайтеся, що всі публічні функції та їхні docstrings відображаються коректно, включаючи параметри та повернені значення.