#!/usr/bin/env python3
"""Заменить стикеры на прямоугольники с золотым сечением"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

PHI = 1.618  # Золотое сечение
HEIGHT = 150
WIDTH = int(HEIGHT * PHI)  # 243

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Получаем все стикеры
items = client.get_items(board_id)
stickers = [i for i in items if i.get('type') == 'sticky_note']

print(f"Найдено стикеров: {len(stickers)}\n")

for i, sticker in enumerate(stickers, 1):
    content = sticker.get('data', {}).get('content', '')
    pos = sticker.get('position', {})
    x, y = pos.get('x', 0), pos.get('y', 0)
    
    # Создаём прямоугольник
    shape = client.create_shape(
        board_id, x, y, WIDTH, HEIGHT, content
    )
    
    # Удаляем стикер
    client.delete_item(board_id, sticker['id'])
    
    print(f"{i}. {content[:40]}...")

print(f"\n✅ Заменено: {len(stickers)}")
