"""
Отладка - проверка карточек
"""
import requests
import csv
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

# Получаем карточки
response = requests.get(
    f"{base_url}/cards?board_id={board_id}", headers=headers
)
cards = response.json()

# Получаем доску
response = requests.get(
    f"{base_url}/boards/{board_id}", headers=headers
)
board = response.json()
columns_map = {col['id']: col['title'] for col in board['columns']}

print(f"Всего карточек: {len(cards)}\n")

# Показываем первые 5 задач (не эпиков)
count = 0
for card in cards:
    if card.get('children_count', 0) == 0:  # Не эпик
        col_name = columns_map.get(card['column_id'], 'Unknown')
        print(f"Колонка: {col_name}")
        print(f"Название: {card['title']}")
        print(f"ID: {card['id']}")
        print()
        count += 1
        if count >= 5:
            break
