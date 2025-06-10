# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
# Додаємо шлях до кореневої директорії вашого проекту, щоб Sphinx міг знаходити модулі.
# '..' означає перейти на один рівень вгору від папки 'docs' (де знаходиться conf.py).
sys.path.insert(0, os.path.abspath('..'))


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
