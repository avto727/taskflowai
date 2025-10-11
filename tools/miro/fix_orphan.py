#!/usr/bin/env python3
"""Найти и переименовать стикер-сироту"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

items = client.get_items(board_id, item_type='sticky_note')

print(f"Всего стикеров: {len(items)}\n")

for item in items:
    content = item.get('data', {}).get('content', '')
    if 'OAuth' in content or 'Авторизация' in content:
        print(f"- {content}")
        
        # Переименовываем если нужно
        if 'OAuth' in content and 'todoist' not in content:
            new_name = "19. Авторизация todoist: OAuth"
            client.update_sticky_note(board_id, item['id'], new_name)
            print(f"  ✅ Переименовал в: {new_name}")
