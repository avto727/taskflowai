#!/usr/bin/env python3
"""Установить цвета эпиков как в Miro"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Читаем roadmap для определения статуса
roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
epic_status = {}

with open(roadmap, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        epic = row['Этап']
        if epic and epic[0].isdigit():
            num = int(epic.split('.')[0])
            done = row['Выполнено'] == '✓'
            if num not in epic_status:
                epic_status[num] = {'total': 0, 'done': 0}
            epic_status[num]['total'] += 1
            if done:
                epic_status[num]['done'] += 1

# Определяем цвет по проценту выполнения
def get_color(num):
    if num not in epic_status:
        return None
    pct = epic_status[num]['done'] / epic_status[num]['total']
    if pct == 1.0:
        return 'green'  # 100%
    elif pct > 0:
        return 'yellow'  # частично
    else:
        return None  # белый (без цвета)

# Получаем карточки
cards = client.get_cards(board_id)

for card in cards:
    name = card['name']
    if name and name[0].isdigit():
        num = int(name.split('.')[0])
        color = get_color(num)
        if color:
            client.set_card_cover(card['id'], color)
            print(f"{name[:50]} → {color}")

print(f"\n✅ Цвета установлены")
