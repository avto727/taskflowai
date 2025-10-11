"""
Перенос готовых эпиков в Готово
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("KAITEN_API_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
base_url = "https://avto727a.kaiten.ru/api/latest"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Получаем доску
response = requests.get(
    f"{base_url}/boards/{board_id}", headers=headers
)
board = response.json()
columns = {col['type']: col['id'] for col in board['columns']}
done_column_id = columns[3]

# Получаем все карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
cards = response.json()

# Находим эпики (карточки, у которых есть дети)
children_ids = {c.get('parent_id') for c in cards if c.get('parent_id')}
epics = [c for c in cards if c['id'] in children_ids]
print(f"Эпиков: {len(epics)}\n")

moved = 0
for epic in epics:
    # Получаем дочерние карточки
    children = [c for c in cards if c.get('parent_id') == epic['id']]
    
    if not children:
        continue
    
    # Проверяем все ли дети в Готово
    all_done = all(c['column_id'] == done_column_id for c in children)
    
    if all_done and epic['column_id'] != done_column_id:
        # Переносим эпик в Готово
        update_data = {"column_id": done_column_id}
        response = requests.patch(
            f"{base_url}/cards/{epic['id']}",
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            moved += 1
            print(f"✅ {epic['title']}")

print(f"\n✅ Эпиков перенесено в Готово: {moved}")
