"""
Перенос готовых карточек в Done
"""
import csv
import os
import sys
from collections import defaultdict

sys.path.append(os.path.dirname(__file__))
from trello_client import TrelloClient

# Читаем roadmap
roadmap_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'roadmap.csv'
)
with open(roadmap_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    tasks = list(reader)

# Группируем по этапам и считаем статусы
stages_status = defaultdict(lambda: {'total': 0, 'done': 0})
for task in tasks:
    stage = task['Этап']
    stages_status[stage]['total'] += 1
    # Задача выполнена только если есть галочка в Выполнено
    if task['Выполнено'].strip() == '✓':
        stages_status[stage]['done'] += 1

# Находим полностью выполненные этапы
done_stages = [
    stage for stage, status in stages_status.items()
    if status['done'] == status['total'] and status['total'] > 0
]

print(f"Полностью выполненных этапов: {len(done_stages)}\n")

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем списки и карточки
lists = client.get_lists(board_id)
done_list_id = lists[2]['id']  # Done
cards = client.get_cards(board_id)

# Переносим готовые карточки
moved = 0
for stage_name in done_stages:
    # Ищем карточку
    card = next((c for c in cards if c['name'] == stage_name), None)
    if card and card['idList'] != done_list_id:
        # Переносим в Done
        import requests
        response = requests.put(
            f"https://api.trello.com/1/cards/{card['id']}",
            params={
                'key': client.api_key,
                'token': client.token,
                'idList': done_list_id
            }
        )
        if response.status_code == 200:
            moved += 1
            print(f"✅ {stage_name}")

print(f"\n✅ Перенесено в Done: {moved}")
