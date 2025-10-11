"""
Перенос готовых эпиков (по названию этапа)
"""
import requests
import csv
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

api_token = os.getenv("KAITEN_API_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
base_url = "https://avto727a.kaiten.ru/api/latest"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

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
    if task['Выполнено'].strip() == '✓':
        stages_status[stage]['done'] += 1

# Находим полностью выполненные этапы
done_stages = [
    stage for stage, status in stages_status.items()
    if status['done'] == status['total'] and status['total'] > 0
]

print(f"Полностью выполненных этапов: {len(done_stages)}\n")

# Получаем доску
response = requests.get(
    f"{base_url}/boards/{board_id}", headers=headers
)
board = response.json()
columns = {col['type']: col['id'] for col in board['columns']}
done_column_id = columns[3]

# Получаем карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
cards = response.json()

# Переносим эпики
moved = 0
for stage_name in done_stages:
    # Ищем карточку-эпик
    epic = next((c for c in cards if c['title'] == stage_name), None)
    if epic and epic['column_id'] != done_column_id:
        update_data = {"column_id": done_column_id}
        response = requests.patch(
            f"{base_url}/cards/{epic['id']}",
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            moved += 1
            print(f"✅ {stage_name}")

print(f"\n✅ Эпиков перенесено: {moved}")
