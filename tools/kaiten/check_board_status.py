"""
Проверка статуса доски
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

board_id = 1518417

response = requests.get(
    f"{base_url}/boards/{board_id}",
    headers=headers
)

board = response.json()

print(f"Доска ID: {board_id}")
print(f"Название: {board.get('title')}")
print(f"Архивная: {board.get('archived', False)}")
print(f"Пространство ID: {board.get('space_id')}")
print(f"\nПолный ответ:")
import json
print(json.dumps(board, indent=2, ensure_ascii=False))
