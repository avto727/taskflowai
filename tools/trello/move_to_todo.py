#!/usr/bin/env python3
"""Переместить карточку в Нужно сделать и переименовать в Н1"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем списки
lists = client.get_lists(board_id)
todo_list = next((l for l in lists if 'Нужно' in l['name']), None)

# Получаем карточку
cards = client.get_cards(board_id)
card = next((c for c in cards if 'Б10' in c['name']), None)

# Переименовываем и перемещаем
new_name = card['name'].replace('Б10', 'Н1')
url = f"{client.base_url}/cards/{card['id']}"
client._request('PUT', url, json={
    'name': new_name,
    'idList': todo_list['id']
})

print(f"✅ Перемещено: {new_name}")
