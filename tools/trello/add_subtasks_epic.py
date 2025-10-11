#!/usr/bin/env python3
"""Добавить эпик Подзадачи и привычки в Бэклог"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем Бэклог
lists = client.get_lists(board_id)
backlog = next((l for l in lists if 'Бэклог' in l['name']), None)

# Создаём карточку
card = client.create_card(
    backlog['id'],
    "Б10. Подзадачи и привычки",
    desc="Поддержка подзадач (parent_id) и recurring задач"
)

# Создаём чеклист
url = f"{client.base_url}/checklists"
checklist = client._request('POST', url, json={
    'idCard': card['id'],
    'name': 'Задачи'
})

# Добавляем пункты
tasks = [
    "Backend: поддержка parent_id в API",
    "Backend: создание подзадач (POST /tasks)",
    "Backend: получение подзадач (GET /tasks?parent_id=X)",
    "Backend: поддержка recurring (due.string)",
    "Bot: команда /subtask для создания подзадачи",
    "Bot: отображение подзадач с отступом",
    "Bot: редактирование подзадач",
    "Bot: удаление подзадач",
    "ИИ: анализ и предложение подзадач",
    "ИИ: шаблоны привычек (утренняя зарядка и т.д.)",
    "Тестирование обычных задач с подзадачами",
    "Тестирование recurring задач с подзадачами"
]

for task in tasks:
    url = f"{client.base_url}/checklists/{checklist['id']}/checkItems"
    client._request('POST', url, json={'name': task})

print(f"✅ Создана карточка: {card['name']}")
print(f"✅ Добавлено задач: {len(tasks)}")
