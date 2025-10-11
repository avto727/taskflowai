#!/usr/bin/env python3
"""Добавить задачи под эпик 1. Подготовка"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

PHI = 1.618
TASK_HEIGHT = 80
TASK_WIDTH = int(TASK_HEIGHT * PHI)  # 129
SPACING = 20

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Находим эпик 1
items = client.get_items(board_id)
shapes = [i for i in items if i.get('type') == 'shape']

epic1 = None
for shape in shapes:
    content = shape.get('data', {}).get('content', '')
    if '1. Подготовка' in content:
        epic1 = shape
        break

if not epic1:
    print("Эпик 1 не найден")
    exit()

epic_pos = epic1.get('position', {})
epic_x = epic_pos.get('x', 0)
epic_y = epic_pos.get('y', 0)

print(f"Эпик 1: x={epic_x}, y={epic_y}\n")

# Читаем задачи эпика 1 из roadmap.csv
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

print(f"Задач: {len(tasks)}\n")

# Рисуем задачи под эпиком
start_y = epic_y + 150 + SPACING

for i, task in enumerate(tasks):
    y = start_y + i * (TASK_HEIGHT + SPACING)
    color = '#d5f692' if task['done'] else '#ffffff'
    
    client.create_shape(
        board_id, epic_x, y, TASK_WIDTH, TASK_HEIGHT,
        task['name']
    )
    client.update_shape_color(board_id, 
        client.get_items(board_id)[-1]['id'], color)
    
    print(f"{i+1}. {task['name'][:40]}...")

print(f"\n✅ Создано задач: {len(tasks)}")
