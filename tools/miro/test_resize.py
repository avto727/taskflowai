#!/usr/bin/env python3
"""Тест изменения размера стикера"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("MIRO_ACCESS_TOKEN")
board_id = os.getenv("MIRO_BOARD_ID")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Получаем первый стикер
r = requests.get(
    f"https://api.miro.com/v2/boards/{board_id}/items",
    headers=headers,
    params={"limit": 50}
)
all_items = r.json().get('data', [])
items = [i for i in all_items if i.get('type') == 'sticky_note']

if not items:
    print("Стикеров нет")
    exit()

item = items[0]
item_id = item['id']
print(f"Стикер: {item.get('data', {}).get('content', '')[:30]}")
print(f"ID: {item_id}\n")

# Пробуем разные варианты изменения размера
tests = [
    {"geometry": {"width": 300, "height": 185}},
    {"style": {"width": "300", "height": "185"}},
    {"width": 300, "height": 185},
]

for i, data in enumerate(tests, 1):
    print(f"Тест {i}: {data}")
    r = requests.patch(
        f"https://api.miro.com/v2/boards/{board_id}/sticky_notes/{item_id}",
        headers=headers,
        json=data
    )
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(f"Error: {r.text[:200]}")
    print()
