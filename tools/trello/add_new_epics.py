#!/usr/bin/env python3
"""Добавить новые эпики в Бэклог"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_TOKEN')
board_id = os.getenv('TRELLO_BOARD_ID')

# Получить Бэклог
url = f'https://api.trello.com/1/boards/{board_id}/lists'
params = {'key': api_key, 'token': token}
lists = requests.get(url, params=params).json()
backlog = next((l for l in lists if 'Бэклог' in l['name']), None)

if not backlog:
    print('❌ Бэклог не найден')
    exit(1)

# Новые эпики
epics = [
    {
        'name': 'Б10. Приоритеты задач (1-4)',
        'desc': '''**Цель:** Присвоить приоритеты 1-4 делам

**Задачи:**
- Backend: поддержка priority в API (уже есть)
- Bot: команда /priority для изменения приоритета
- Bot: отображение приоритета (🔴🟡🟢⚪)
- ИИ: автоопределение приоритета при создании
- Фильтрация по приоритету
- Сортировка по приоритету'''
    },
    {
        'name': 'Б11. Гео-триггеры',
        'desc': '''**Цель:** Включение дел по геолокации

**Задачи:**
- Backend: хранение геолокаций для задач
- Backend: API для геотриггеров
- Bot: команда /location для привязки места
- Bot: определение текущей геолокации
- Триггер: напоминание при приходе на работу
- Настройка радиуса срабатывания
- История срабатываний'''
    },
    {
        'name': 'Б12. Квадрат Эйзенхауэра (Web)',
        'desc': '''**Цель:** UI с квадратом Эйзенхауэра в Web App

**Задачи:**
- Web: компонент квадрата (4 квадранта)
- Web: drag & drop задач между квадрантами
- Web: автоматическое изменение приоритета
- Web: фильтры по квадрантам
- Интеграция с Todoist priority
- Визуализация (цвета, иконки)'''
    },
    {
        'name': 'Б13. Три важные задачи дня',
        'desc': '''**Цель:** Выделение 3 важных задач на день

**Задачи:**
- Backend: метка "важная задача дня"
- Backend: API для назначения важных задач
- Bot: команда /important для назначения
- Bot: отображение важных задач отдельно
- ИИ: предложение важных задач на день
- Ограничение: максимум 3 задачи
- Утреннее напоминание о важных задачах'''
    }
]

# Создать карточки
for epic in epics:
    url = 'https://api.trello.com/1/cards'
    data = {
        'idList': backlog['id'],
        'name': epic['name'],
        'desc': epic['desc'],
        'key': api_key,
        'token': token
    }
    response = requests.post(url, params=data)
    if response.status_code == 200:
        print(f'✅ {epic["name"]}')
    else:
        print(f'❌ Ошибка: {epic["name"]}')

print('\n✅ Все эпики добавлены в Бэклог!')
