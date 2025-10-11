#!/usr/bin/env python3
"""Исправить цвета и добавить стрелки"""
import sys
from pathlib import Path
import csv
sys.path.append(str(Path(__file__).parent.parent))

from miro.miro_client import MiroClient
import os

client = MiroClient()
board_id = os.getenv("MIRO_BOARD_ID")

# Читаем статусы из roadmap.csv
roadmap = Path(__file__).parent.parent.parent / "roadmap.csv"
epic_status = {}

with open(roadmap, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stage = row['Этап']
        done = row['Выполнено'] == '✓'
        
        if stage not in epic_status:
            epic_status[stage] = {'tasks': [], 'done': 0}
        epic_status[stage]['tasks'].append(done)
        if done:
            epic_status[stage]['done'] += 1

# Определяем цвет для каждого эпика
colors = {}
for stage, data in epic_status.items():
    total = len(data['tasks'])
    done = data['done']
    percent = (done / total * 100) if total else 0
    
    if percent == 100:
        colors[stage] = '#d5f692'  # Зелёный
    elif percent > 0:
        colors[stage] = '#fef445'  # Жёлтый
    else:
        colors[stage] = '#ffffff'  # Белый

# Получаем shapes
items = client.get_items(board_id)
shapes = sorted(
    [i for i in items if i.get('type') == 'shape'],
    key=lambda x: x.get('position', {}).get('x', 0)
)

print(f"Найдено shapes: {len(shapes)}\n")

# Обновляем цвета
for shape in shapes:
    content = shape.get('data', {}).get('content', '')
    
    # Ищем эпик по имени
    for epic, color in colors.items():
        if epic in content or content in epic:
            client.update_shape_color(
                board_id, shape['id'], color
            )
            print(f"✓ {content[:40]}... → {color}")
            break

# Создаём стрелки
print(f"\n➡️  Создаю стрелки...")
for i in range(len(shapes) - 1):
    client.create_connector(
        board_id, shapes[i]['id'], shapes[i+1]['id']
    )
    print(f"  {i+1} → {i+2}")

print(f"\n✅ Готово!")
