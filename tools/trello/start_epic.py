#!/usr/bin/env python3
"""Переместить Н1 в В процессе"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from trello.trello_client import TrelloClient
import os

client = TrelloClient()
board_id = os.getenv("TRELLO_BOARD_ID")

lists = client.get_lists(board_id)
in_progress = next((l for l in lists if 'процессе' in l['name']), None)

cards = client.get_cards(board_id)
card = next((c for c in cards if 'Н1' in c['name']), None)

url = f"{client.base_url}/cards/{card['id']}"
client._request('PUT', url, json={'idList': in_progress['id']})

print(f"✅ {card['name']} → В процессе")
