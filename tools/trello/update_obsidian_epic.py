#!/usr/bin/env python3
"""Обновить эпик Obsidian - добавить граф знаний"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_TOKEN')
board_id = os.getenv('TRELLO_BOARD_ID')

# Получить карточку Б19
url = f'https://api.trello.com/1/boards/{board_id}/cards'
params = {'key': api_key, 'token': token}
cards = requests.get(url, params=params).json()
b19 = next((c for c in cards if 'Б19.' in c['name']), None)

if not b19:
    print('❌ Карточка Б19 не найдена')
    exit(1)

# Обновлённое описание (короткая версия)
new_desc = '''**Цель:** Граф знаний вместо иерархии

**Ключевая идея:**
Todoist: задача в ОДНОЙ категории
Obsidian: заметка в НЕСКОЛЬКИХ категориях через теги

**Пример:**
"Баня с женой" → #семья #здоровье #деньги
Видна из всех 3 категорий!

**Задачи:**
- Экспорт категорий в Markdown
- Заметки с множественными тегами
- ИИ определяет все релевантные категории
- Команда /export_obsidian
- Граф связей между категориями
- Анализ паттернов

**Преимущества:**
✅ Многомерность
✅ Естественность
✅ Инсайты через граф

**Оценка:** 4-5 дней

Подробнее: tools/obsidian/CONCEPT.md'''

# Обновить
url = f'https://api.trello.com/1/cards/{b19["id"]}'
data = {'desc': new_desc, 'key': api_key, 'token': token}
response = requests.put(url, params=data)

if response.status_code == 200:
    print('✅ Эпик Б19 обновлён: добавлен граф знаний')
else:
    print(f'❌ Ошибка: {response.status_code}')
