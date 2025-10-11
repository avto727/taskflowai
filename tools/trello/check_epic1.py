#!/usr/bin/env python3
"""Проверить чеклист эпика 1"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Читаем roadmap
roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
print("Задачи эпика 1 в roadmap.csv:\n")

with open(roadmap, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Этап'] == '1. Подготовка':
            done = '✓' if row['Выполнено'] == '✓' else '✗'
            print(f"{done} {row['Задача']}")

# Получаем карточку эпика 1
cards = client.get_cards(board_id)
epic1 = next((c for c in cards if c['name'].startswith('1.')), None)

if epic1:
    print(f"\n\nЧеклист в Trello (карточка {epic1['name']}):\n")
    
    # Получаем чеклисты
    url = f"{client.base_url}/cards/{epic1['id']}/checklists"
    resp = client._request('GET', url)
    
    for checklist in resp:
        for item in checklist['checkItems']:
            done = '✓' if item['state'] == 'complete' else '✗'
            print(f"{done} {item['name']}")
