#!/usr/bin/env python3
"""Добавить эпик по интеграции с Obsidian"""
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

# Новый эпик
epic = {
    'name': 'Б19. Интеграция с Obsidian',
    'desc': '''**Цель:** Перенос категорий и подкатегорий в Obsidian

**Что делаем:**
Создаём структуру знаний в Obsidian на базе категорий TaskFlowAI.
Obsidian = база знаний, Todoist = задачи, связь через теги и ссылки.

**Структура в Obsidian:**
```
TaskFlowAI/
├── Категории/
│   ├── 💰 Деньги.md
│   │   ├── Зарплата
│   │   ├── Инвестиции
│   │   └── Бюджет
│   ├── 👨‍👩‍👧 Семья.md
│   ├── 🏥 Здоровье.md
│   ├── 🤝 Взаимоотношения.md
│   └── 🧘 Развитие.md
└── Задачи/
    └── (синхронизация с Todoist)
```

**Задачи:**
- Backend: экспорт категорий в Markdown
- Backend: создание структуры папок/файлов
- Backend: генерация ссылок между заметками
- Bot: команда /export_obsidian
- Шаблоны заметок для категорий
- Автообновление при изменении категорий
- Связь задач Todoist с заметками Obsidian

**Формат заметки категории:**
```markdown
# 💰 Деньги

## Подкатегории
- [[Зарплата]]
- [[Инвестиции]]
- [[Бюджет]]

## Активные задачи
- [ ] Задача 1 (Todoist ID: 123)
- [ ] Задача 2 (Todoist ID: 456)

## Заметки
...
```

**Преимущества:**
- Obsidian для долгосрочных знаний и планирования
- Todoist для краткосрочных задач и выполнения
- Связь через теги и ID задач
- Markdown = универсальный формат

**Технические детали:**
- Obsidian работает с локальными Markdown файлами
- Можно использовать Obsidian API (плагины)
- Или просто генерировать .md файлы в папку Obsidian

**Связи:**
- Дополняет Б15 (Inbox + Project)
- Использует категории из backend

**Ценность:**
База знаний + система задач = полная картина жизни

**Оценка:** 3-4 дня'''
}

# Создать карточку
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

print('\n✅ Эпик по Obsidian добавлен в Бэклог!')
