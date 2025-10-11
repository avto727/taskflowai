#!/usr/bin/env python3
"""Центрировать текст в прямоугольниках"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

items = client.get_items(board_id)
shapes = [i for i in items if i.get('type') == 'shape']

print(f"Найдено shapes: {len(shapes)}\n")

for shape in shapes:
    content = shape.get('data', {}).get('content', '')
    client.center_shape_text(board_id, shape['id'])
    print(f"✓ {content[:40]}...")

print(f"\n✅ Центрировано: {len(shapes)}")
