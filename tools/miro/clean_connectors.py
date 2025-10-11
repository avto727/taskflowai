#!/usr/bin/env python3
"""Удалить все стрелки (connectors) с доски"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Получаем connectors напрямую
items = client.get_connectors(board_id)

print(f"Найдено стрелок: {len(items)}")

if items:
    print("Удаляю...")
    for item in items:
        try:
            client.delete_connector(board_id, item['id'])
            print(".", end="", flush=True)
        except Exception as e:
            print(f"\n⚠️  {e}")
    print(f"\n✅ Удалено: {len(items)}")
else:
    print("Стрелок нет")
