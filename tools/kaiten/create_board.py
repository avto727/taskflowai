"""
Создание новой доски в пространстве
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("KAITEN_API_TOKEN")
base_url = "https://avto727a.kaiten.ru/api/latest"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Получаем пространства
response = requests.get(f"{base_url}/spaces", headers=headers)
spaces = response.json()

print("Пространства:")
for space in spaces:
    print(f"  ID: {space['id']}, Название: {space['title']}")

# Берем первое пространство
space_id = spaces[0]['id']
print(f"\nИспользуем пространство ID: {space_id}")

# Создаем доску с колонками
board_data = {
    "title": "TasksFlow Dev",
    "columns": [
        {"title": "Очередь", "type": 1},
        {"title": "В работе", "type": 2},
        {"title": "Готово", "type": 3}
    ],
    "lanes": [
        {"title": "Default"}
    ]
}

response = requests.post(
    f"{base_url}/spaces/{space_id}/boards",
    headers=headers,
    json=board_data
)

print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")

if response.status_code not in [200, 201]:
    print(f"❌ Ошибка создания доски")
    exit(1)

board = response.json()
board_id = board['id']

print(f"\n✅ Доска создана!")
print(f"ID: {board_id}")
print(f"Название: {board['title']}")
print(f"Ссылка: https://avto727a.kaiten.ru/space/{space_id}/board/{board_id}")

# Получаем колонки
columns = board.get('columns', [])
if columns:
    column_id = columns[0]['id']
    print(f"\nКолонка ID: {column_id}")
    
    # Создаем тестовую карточку
    card_data = {
        "board_id": board_id,
        "column_id": column_id,
        "title": "Тестовая карточка"
    }
    
    response = requests.post(
        f"{base_url}/cards",
        headers=headers,
        json=card_data
    )
    
    print("✅ Тестовая карточка создана!")
