#!/usr/bin/env python3
"""Перенумеровать карточки: Готово → Г1-Г12, Бэклог → Б1-Б9"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

# Получаем списки и карточки
lists = client.get_lists(board_id)
cards = client.get_cards(board_id)

done_list = next((l for l in lists if 'Готово' in l['name']), None)
backlog_list = next((l for l in lists if 'Бэклог' in l['name']), None)

# Карточки в Готово (сортируем по позиции)
done_cards = [c for c in cards if c['idList'] == done_list['id']]
done_cards.sort(key=lambda x: x['pos'])

# Карточки в Бэклог
backlog_cards = [c for c in cards if c['idList'] == backlog_list['id']]
backlog_cards.sort(key=lambda x: x['pos'])

# Перенумеровываем Готово
for i, card in enumerate(done_cards, 1):
    old_name = card['name']
    # Убираем старый номер
    new_name = old_name.split('.', 1)[1].strip() if '.' in old_name else old_name
    new_name = f"Г{i}. {new_name}"
    
    url = f"{client.base_url}/cards/{card['id']}"
    client._request('PUT', url, json={'name': new_name})
    print(f"{old_name[:40]} → {new_name[:40]}")

print()

# Перенумеровываем Бэклог
for i, card in enumerate(backlog_cards, 1):
    old_name = card['name']
    new_name = old_name.split('.', 1)[1].strip() if '.' in old_name else old_name
    new_name = f"Б{i}. {new_name}"
    
    url = f"{client.base_url}/cards/{card['id']}"
    client._request('PUT', url, json={'name': new_name})
    print(f"{old_name[:40]} → {new_name[:40]}")

print(f"\n✅ Готово: {len(done_cards)} карточек")
print(f"✅ Бэклог: {len(backlog_cards)} карточек")
