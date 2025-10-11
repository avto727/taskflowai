#!/usr/bin/env python3
"""Проверить все элементы на доске"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

all_items = client.get_items(board_id)

types = {}
for item in all_items:
    t = item.get('type', 'unknown')
    types[t] = types.get(t, 0) + 1

print(f"Всего элементов: {len(all_items)}\n")
for t, count in sorted(types.items()):
    print(f"{t}: {count}")
