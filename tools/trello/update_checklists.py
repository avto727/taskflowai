"""
Обновление чеклистов в карточках
"""
import csv
import os
import sys
from collections import defaultdict
import requests

sys.path.append(os.path.dirname(__file__))
from trello_client import TrelloClient

# Читаем roadmap
roadmap_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)
with open(roadmap_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    tasks = list(reader)

# Группируем по этапам
stages = defaultdict(list)
for task in tasks:
    stages[task['Этап']].append(task)

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")
cards = client.get_cards(board_id)

updated = 0
for stage_name, stage_tasks in stages.items():
    # Находим карточку
    card = next((c for c in cards if c['name'] == stage_name), None)
    if not card:
        continue
    
    # Обновляем описание с правильными галочками
    desc = f"**Задач:** {len(stage_tasks)}\n\n"
    desc += "**Чеклист:**\n"
    for task in stage_tasks:
        # Задача выполнена только если есть галочка в Выполнено
        is_done = task['Выполнено'].strip() == '✓'
        status = "✅" if is_done else "⬜"
        desc += f"{status} {task['Задача']}\n"
    
    # Обновляем карточку
    response = requests.put(
        f"https://api.trello.com/1/cards/{card['id']}",
        params={
            'key': client.api_key,
            'token': client.token,
            'desc': desc
        }
    )
    if response.status_code == 200:
        updated += 1
        done_count = sum(1 for t in stage_tasks 
                        if t['Выполнено'].strip() == '✓')
        print(f"✅ {stage_name} ({done_count}/{len(stage_tasks)})")

print(f"\n✅ Обновлено карточек: {updated}")
