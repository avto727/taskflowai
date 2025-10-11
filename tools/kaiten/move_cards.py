"""
Перенос карточек между досками
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

old_board_id = 1518417
new_board_id = 1518905

# Получаем карточки старой доски
response = requests.get(
    f"{base_url}/cards?board_id={old_board_id}",
    headers=headers
)
old_cards = response.json()

# Получаем колонки новой доски
response = requests.get(
    f"{base_url}/boards/{new_board_id}",
    headers=headers
)
new_board = response.json()
new_columns = {col['type']: col['id'] for col in new_board['columns']}

print(f"Карточек для переноса: {len(old_cards)}")

moved = 0
for card in old_cards:
    # Определяем колонку по типу
    old_col_type = card.get('column', {}).get('type', 1)
    new_column_id = new_columns.get(old_col_type, new_columns[1])
    
    # Переносим карточку
    update_data = {
        "board_id": new_board_id,
        "column_id": new_column_id
    }
    
    response = requests.patch(
        f"{base_url}/cards/{card['id']}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        moved += 1
        print(f"✅ {card['title'][:50]}")
    else:
        print(f"❌ {card['title'][:50]}: {response.status_code}")

print(f"\n✅ Перенесено: {moved}/{len(old_cards)}")
