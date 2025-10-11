"""
Пересоздание структуры с эпиками
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
    stage = task['Этап']
    stages[stage].append(task)

print(f"Этапов: {len(stages)}")
print(f"Задач: {len(tasks)}")

# Получаем доску
response = requests.get(
    f"{base_url}/boards/{board_id}", headers=headers
)
board = response.json()
columns = {col['type']: col['id'] for col in board['columns']}
lane_id = board['lanes'][0]['id']

# Удаляем старые карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
old_cards = response.json()
print(f"\nУдаляю {len(old_cards)} старых карточек...")
for card in old_cards:
    requests.delete(
        f"{base_url}/cards/{card['id']}", headers=headers
    )

# Создаём эпики и задачи
print("\nСоздаю структуру...")
for stage_name in sorted(stages.keys()):
    stage_tasks = stages[stage_name]
    
    # Создаём эпик
    epic_data = {
        "board_id": board_id,
        "column_id": columns[1],
        "lane_id": lane_id,
        "title": stage_name
    }
    response = requests.post(
        f"{base_url}/cards", headers=headers, json=epic_data
    )
    epic = response.json()
    print(f"\n📦 {stage_name}")
    
    # Создаём задачи
    for task in stage_tasks:
        # Определяем колонку
        if task['Выполнено']:
            col_id = columns[3]
        elif task['В процессе']:
            col_id = columns[2]
        else:
            col_id = columns[1]
        
        task_data = {
            "board_id": board_id,
            "column_id": col_id,
            "lane_id": lane_id,
            "title": task['Задача'],
            "parent_id": epic['id']
        }
        requests.post(
            f"{base_url}/cards", headers=headers, json=task_data
        )
        print(f"  ├─ {task['Задача'][:50]}")

print("\n✅ Структура создана!")
