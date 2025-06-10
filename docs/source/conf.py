# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Отримуємо абсолютний шлях до директорії, де знаходиться цей conf.py (тобто, папка 'docs/source')
conf_dir = os.path.dirname(__file__)

# Піднімаємося на два рівні вгору, щоб отримати шлях до кореневої директорії проєкту (TGBOTTARAS)
# Потім додаємо 'for_test' до цього шляху, щоб Sphinx міг імпортувати модулі.
project_source_path = os.path.abspath(os.path.join(conf_dir, os.pardir, os.pardir, 'for_test'))

# Вставляємо шлях до директорії з модулями на початок sys.path
sys.path.insert(0, project_source_path)

# ==============================================================================
# ДІАГНОСТИЧНІ ВИВОДИ (ВИДАЛИТИ ПІСЛЯ ВИПРАВЛЕННЯ ПРОБЛЕМИ З ІМПОРТОМ)
# Ці рядки допоможуть нам побачити, які шляхи використовуються
print(f"DEBUG: conf.py path: {conf_dir}")
print(f"DEBUG: Project source path calculated: {project_source_path}")
print(f"DEBUG: sys.path after modification: {sys.path[0]}")
print(f"DEBUG: os.getcwd() (current working directory): {os.getcwd()}")
# ==============================================================================


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Telegram Bot для Судових Установ'
copyright = '2025, Makarenko Taras' # Замініть на ваше ім'я
author = 'Makarenko Taras' # Замініть на ваше ім'я
release = '1.0.0' # Версія проєкту

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Додайте необхідні розширення Sphinx
extensions = [
    'sphinx.ext.autodoc',     # Для автоматичного витягування docstrings
    'sphinx.ext.napoleon',    # Для підтримки Google/NumPy style docstrings
    'sphinx.ext.viewcode',    # Для генерації посилань на вихідний код
    'sphinx.ext.todo',        # Для відображення "todo" нотаток у документації
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Встановлення мови документації
language = 'uk'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Встановлення теми оформлення
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Налаштування для розширення todo
todo_include_todos = True
