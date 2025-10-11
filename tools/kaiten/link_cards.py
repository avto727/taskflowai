"""
Связывание карточек в иерархию
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

# Группируем по этапам
stages = defaultdict(list)
for task in tasks:
    stages[task['Этап']].append(task['Задача'])

# Получаем карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
cards = response.json()

# Создаём словарь: название → id
cards_map = {c['title']: c['id'] for c in cards}

# Связываем
linked = 0
for stage_name, task_names in stages.items():
    if stage_name not in cards_map:
        print(f"⚠️ Эпик не найден: {stage_name}")
        continue
    
    epic_id = cards_map[stage_name]
    
    for task_name in task_names:
        if task_name in cards_map:
            task_id = cards_map[task_name]
            # Связываем через parents_ids
            update_data = {"parents_ids": [epic_id]}
            response = requests.patch(
                f"{base_url}/cards/{task_id}",
                headers=headers,
                json=update_data
            )
            if response.status_code == 200:
                linked += 1

print(f"✅ Связано карточек: {linked}")
