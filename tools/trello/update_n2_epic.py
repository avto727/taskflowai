#!/usr/bin/env python3
"""Обновить эпик Н2 - универсальная календарная синхронизация"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_TOKEN')
board_id = os.getenv('TRELLO_BOARD_ID')

# Получить все карточки
url = f'https://api.trello.com/1/boards/{board_id}/cards'
params = {'key': api_key, 'token': token}
cards = requests.get(url, params=params).json()

# Найти карточку Н2
n2_card = next((c for c in cards if 'Н2.' in c['name']), None)

if not n2_card:
    print('❌ Карточка Н2 не найдена')
    exit(1)

# Новое описание
new_name = 'Н2. Синхронизация с календарями'
new_desc = '''**Цель:** Настройка синхронизации задач с любым календарём

**Что делаем:**
Todoist имеет встроенную интеграцию с календарями через iCal feed.
Добавляем удобную настройку этой функции через бот.

**Поддерживаемые календари:**
- ✅ Google Calendar
- ✅ Apple Calendar (iCal)
- ✅ Outlook Calendar
- ✅ Любой календарь с поддержкой iCal

**Задачи:**
- Backend: получение iCal feed URL из Todoist API
- Backend: настройка фильтров синхронизации
- Bot: команда /calendar - показать инструкцию
- Bot: команда /calendar_url - получить ссылку для подключения
- Bot: выбор проектов для синхронизации
- Инструкции для разных календарей (Google/Apple/Outlook)
- FAQ по настройке

**Как работает:**
1. Пользователь получает iCal feed URL через бот
2. Подключает этот URL к своему календарю
3. Задачи с датами автоматически появляются в календаре
4. Обновления синхронизируются автоматически

**Преимущества подхода:**
- ✅ Работает с любым календарём
- ✅ Не нужна OAuth авторизация
- ✅ Использует встроенный функционал Todoist
- ✅ Быстрая реализация (1-2 дня вместо 3-4)

**Ценность:**
Пользователи видят задачи в привычном календаре,
планируют день с учётом встреч и задач.

**Оценка:** 1-2 дня (упрощённая реализация)'''

# Обновить карточку
url = f'https://api.trello.com/1/cards/{n2_card["id"]}'
data = {
    'name': new_name,
    'desc': new_desc,
    'key': api_key,
    'token': token
}
response = requests.put(url, params=data)

if response.status_code == 200:
    print(f'✅ Карточка обновлена: {new_name}')
    print(f'\nИзменения:')
    print(f'- Название: "{n2_card["name"]}" → "{new_name}"')
    print(f'- Подход: Google Calendar API → iCal feed (универсально)')
    print(f'- Оценка: 3-4 дня → 1-2 дня')
else:
    print(f'❌ Ошибка обновления: {response.status_code}')

print('\n✅ Эпик Н2 обновлён!')
