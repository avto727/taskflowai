#!/usr/bin/env python3
"""Добавить колонку Бэклог и переместить эпики"""
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

# Создаём Бэклог первым
backlog = client.create_list(board_id, "Бэклог", pos="top")
print(f"✅ Создана колонка: {backlog['name']}")

# Получаем карточки
cards = client.get_cards(board_id)

# Эпики для переноса: 7-9, 16-21
epic_nums = [7, 8, 9, 16, 17, 18, 19, 20, 21]

moved = 0
for card in cards:
    name = card['name']
    # Проверяем номер эпика
    if name and name[0].isdigit():
        num = int(name.split('.')[0])
        if num in epic_nums:
            client.move_card(card['id'], backlog['id'])
            print(f"Перенёс: {name[:50]}")
            moved += 1

print(f"\n✅ Перенесено {moved} эпиков в Бэклог")
