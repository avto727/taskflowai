#!/usr/bin/env python3
"""Создание новых эпиков в Бэклоге"""
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
        'name': 'Б14. Система поощрений Todoist',
        'desc': '''**Цель:** Повторение системы karma/achievements

**Задачи:**
- Backend: получение karma через API
- Backend: расчёт streak (серии дней)
- Bot: команда /karma
- Bot: уведомления о достижениях
- Визуализация уровней (Beginner→Expert→Master)
- Статистика по дням/неделям

**Ценность:** Геймификация = мотивация

**Оценка:** 2-3 дня'''
    },
    {
        'name': 'Б15. Inbox + Project (Trello)',
        'desc': '''**Цель:** Inbox для быстрого сбора + проекты

**Концепция:** См. tools/trello/INBOX_PROJECT_CONCEPT.txt

**Задачи (MVP):**
- Backend: поддержка Inbox проекта
- Bot: команда /inbox
- Bot: команда /review
- ИИ: анализ "задача vs проект"
- ИИ: предложение категории/приоритета

**Интеграция с Trello:** ⏳ Теоретический прототип

**Оценка:** MVP 3-4 дня, Full 1-2 недели'''
    },
    {
        'name': 'Б16. Ритуалы как триггеры',
        'desc': '''**Цель:** Контекстное переключение через ритуалы

**Примеры:**
- Утренний ритуал → блок "Утренние дела"
- Приход на работу → блок "Рабочие задачи"
- Вечер → блок "Вечерняя рутина"

**Задачи:**
- Backend: модель Ritual
- Backend: триггеры (время/место/действие)
- Bot: команда /ritual
- Bot: настройка ритуалов
- Автопоказ блока задач при триггере
- Чеклист для ритуала
- Интеграция с гео-триггерами (Б11)

**Связи:** Использует шаблоны (Б17)

**Оценка:** 4-5 дней'''
    },
    {
        'name': 'Б17. Шаблоны',
        'desc': '''**Цель:** Библиотека шаблонов для быстрого создания

**Примеры:**
- "Утренняя зарядка" → 5 подзадач
- "Поездка" → чеклист сборов
- "Проект" → структура задач

**Задачи:**
- Backend: модель Template
- Backend: CRUD для шаблонов
- Bot: команда /templates
- Bot: создание шаблона
- Bot: применение шаблона
- ИИ: предложение подходящего шаблона
- Библиотека стандартных шаблонов

**Связи:** База для ритуалов (Б16)

**Оценка:** 3-4 дня'''
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
