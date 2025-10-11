#!/usr/bin/env python3
"""Исправить задачи под эпик 1"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

EPIC_WIDTH = 243
EPIC_HEIGHT = 150
TASK_WIDTH = EPIC_WIDTH
TASK_HEIGHT = EPIC_HEIGHT // 3  # 50
SPACING = 10
EPIC_TO_TASK_SPACING = SPACING  # Отступ эпик→задача = задача→задача

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Удаляем старые задачи (маленькие shapes под эпиком 1)
items = client.get_items(board_id)
shapes = [i for i in items if i.get('type') == 'shape']

epic1 = None
for s in shapes:
    if '1. Подготовка' in s.get('data', {}).get('content', ''):
        epic1 = s
        break

epic_x = epic1.get('position', {}).get('x', 0)
epic_y = epic1.get('position', {}).get('y', 0)

# Удаляем задачи (shapes ниже эпика)
for s in shapes:
    sy = s.get('position', {}).get('y', 0)
    sx = s.get('position', {}).get('x', 0)
    if abs(sx - epic_x) < 50 and sy > epic_y + 100:
        client.delete_item(board_id, s['id'])
        print(f"Удалил: {s.get('data', {}).get('content', '')[:30]}")

# Читаем задачи
roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
tasks = []
with open(roadmap, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Этап'] == '1. Подготовка':
            tasks.append({
                'name': row['Задача'],
                'done': row['Выполнено'] == '✓'
            })

# Создаём новые задачи
print(f"\nСоздаю {len(tasks)} задач:\n")
start_y = epic_y + EPIC_HEIGHT/2 + TASK_HEIGHT/2 + SPACING

for i, task in enumerate(tasks):
    y = start_y + i * (TASK_HEIGHT + SPACING)
    color = '#d5f692' if task['done'] else '#ffffff'
    
    shape = client.create_rounded_shape(
        board_id, epic_x, y, TASK_WIDTH, TASK_HEIGHT,
        task['name'], color
    )
    print(f"{i+1}. {task['name'][:40]}...")

print(f"\n✅ Готово!")
